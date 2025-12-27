"""Voice output module - Speaks announcements and descriptions using TTS."""

import asyncio
import logging
import queue
import threading
from typing import Optional, List
from modules.base import BaseModule
from contracts.schemas import FusionAnnouncement, SceneDescription
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 not installed (pip install pyttsx3)")


class VoiceOutputModule(BaseModule):
    """
    Voice output module.
    
    Subscribes to FusionAnnouncement and SceneDescription events
    and speaks them using text-to-speech.
    
    Uses pyttsx3 for offline TTS (no internet required).
    """
    
    name = "VoiceOutput"
    
    def __init__(
        self,
        enabled: bool = True,
        rate: int = 175,  # Words per minute
        volume: float = 0.9,  # 0.0 to 1.0
        voice_gender: str = "female",  # "male" or "female"
        interrupt_mode: bool = False  # If True, interrupt current speech for new announcements
    ):
        """
        Initialize voice output module.
        
        Args:
            enabled: Whether voice output is enabled
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_gender: Preferred voice gender
            interrupt_mode: If True, new announcements interrupt current speech
        """
        self.enabled = enabled
        self.rate = rate
        self.volume = volume
        self.voice_gender = voice_gender
        self.interrupt_mode = interrupt_mode
        self.running = False
        self.result_bus: Optional[ResultBus] = None
        self.control_state: Optional[ControlState] = None
        self.is_speaking = False  # Track if TTS is currently speaking
        
        if not TTS_AVAILABLE:
            self.enabled = False
            logger.warning("Voice output disabled - pyttsx3 not available")
        
        if self.enabled:
            # TTS engine must run in separate thread
            self.speech_queue = queue.Queue(maxsize=1)  # Only hold 1 item max!
            self.tts_thread = None
            self._init_tts_engine()
    
    def _init_tts_engine(self) -> None:
        """Initialize TTS engine in background thread."""
        def tts_worker():
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)
            
            # Set voice
            voices = engine.getProperty('voices')
            for voice in voices:
                if self.voice_gender.lower() in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            logger.info(f"TTS engine initialized (rate: {self.rate}, volume: {self.volume})")
            
            while self.running:
                try:
                    # Block until we get something to say (with timeout)
                    text = self.speech_queue.get(timeout=0.5)
                    
                    if text:
                        self.is_speaking = True
                        logger.info(f"🔊 Speaking: {text}")
                        engine.say(text)
                        engine.runAndWait()
                        self.is_speaking = False
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"TTS error: {e}")
                    self.is_speaking = False
        
        self.tts_thread = threading.Thread(target=tts_worker, daemon=True)
    
    async def start(
        self,
        frame_bus,  # Not used
        result_bus: ResultBus,
        control_state: ControlState,
    ) -> List[asyncio.Task]:
        """Start the module."""
        self.result_bus = result_bus
        self.control_state = control_state
        self.running = True
        
        if not self.enabled:
            logger.info(f"{self.name} module disabled")
            return []
        
        # Start TTS thread
        self.tts_thread.start()
        
        tasks = [
            asyncio.create_task(self._speak_announcements()),
            asyncio.create_task(self._speak_descriptions()),
        ]
        
        logger.info(f"{self.name} module started")
        return tasks
    
    async def _speak_announcements(self) -> None:
        """Speak fusion announcements."""
        try:
            async for announcement in self.result_bus.subscribe_type(FusionAnnouncement):
                if not self.running:
                    break
                
                if self.control_state.paused:
                    continue
                
                # If currently speaking, skip this announcement (don't interrupt)
                if self.is_speaking:
                    continue
                
                # Try to add to queue (will fail if full, which is what we want)
                try:
                    self.speech_queue.put_nowait(announcement.text)
                except queue.Full:
                    # Queue is full (already has 1 item), skip this announcement
                    pass
        
        except Exception as e:
            logger.error(f"{self.name} announcement error: {e}", exc_info=True)
    
    async def _speak_descriptions(self) -> None:
        """Speak scene descriptions."""
        try:
            async for description in self.result_bus.subscribe_type(SceneDescription):
                if not self.running:
                    break
                
                if self.control_state.paused:
                    continue
                
                # Scene descriptions have higher priority - always try to speak them
                # But wait if currently speaking
                while self.is_speaking and self.running:
                    await asyncio.sleep(0.1)
                
                # Clear the queue and add this description
                try:
                    while not self.speech_queue.empty():
                        self.speech_queue.get_nowait()
                except queue.Empty:
                    pass
                
                # Queue for speech
                try:
                    self.speech_queue.put_nowait(description.description)
                except queue.Full:
                    pass  # Shouldn't happen since we just cleared it
        
        except Exception as e:
            logger.error(f"{self.name} description error: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Stop the module."""
        self.running = False
        if self.enabled and hasattr(self, 'tts_thread') and self.tts_thread:
            self.tts_thread.join(timeout=2)
        logger.info(f"{self.name} module stopped")

