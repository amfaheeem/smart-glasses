"""Voice input module - Receives voice commands via speech recognition."""

import asyncio
import logging
from typing import Optional, List
from modules.base import BaseModule
from contracts.schemas import ControlEvent
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition not installed (pip install SpeechRecognition pyaudio)")


class VoiceInputModule(BaseModule):
    """
    Voice input module.
    
    Listens for voice commands and publishes ControlEvent messages.
    
    Supported commands:
    - "pause" / "stop" → Pause video
    - "resume" / "continue" / "play" → Resume video
    - "describe" / "what do you see" → Trigger scene description
    - "quit" / "exit" → Shutdown system
    """
    
    name = "VoiceInput"
    
    def __init__(
        self,
        enabled: bool = True,
        language: str = "en-US",
        timeout: float = 5.0
    ):
        """
        Initialize voice input module.
        
        Args:
            enabled: Whether voice input is enabled
            language: Language code (en-US, ar-SA, etc.)
            timeout: Timeout for listening (seconds)
        """
        self.enabled = enabled
        self.language = language
        self.timeout = timeout
        self.running = False
        self.result_bus: Optional[ResultBus] = None
        self.control_state: Optional[ControlState] = None
        
        if not SPEECH_RECOGNITION_AVAILABLE:
            self.enabled = False
            logger.warning("Voice input disabled - speech_recognition not available")
        
        if self.enabled:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
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
        
        task = asyncio.create_task(self._listen_for_commands())
        logger.info(f"{self.name} module started (language: {self.language})")
        logger.info("Voice commands: 'pause', 'resume', 'describe', 'quit'")
        return [task]
    
    async def _listen_for_commands(self) -> None:
        """Listen for voice commands in background."""
        try:
            while self.running:
                # Listen in thread pool to avoid blocking
                command = await asyncio.get_event_loop().run_in_executor(
                    None, self._listen_once
                )
                
                if command:
                    await self._process_command(command)
        
        except Exception as e:
            logger.error(f"{self.name} error: {e}", exc_info=True)
    
    def _listen_once(self) -> Optional[str]:
        """Listen for one command (blocking)."""
        try:
            with self.microphone as source:
                logger.debug("Listening for command...")
                audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=3)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Heard: '{text}'")
            return text.lower()
        
        except sr.WaitTimeoutError:
            # No speech detected, normal
            return None
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            return None
    
    async def _process_command(self, command: str) -> None:
        """Process recognized voice command."""
        command = command.strip().lower()
        
        # Pause commands
        if any(word in command for word in ["pause", "stop", "wait"]):
            event = ControlEvent(kind="pause", value=True)
            await self.result_bus.publish(event)
            logger.info("🎤 Voice command: PAUSE")
        
        # Resume commands
        elif any(word in command for word in ["resume", "continue", "play", "go"]):
            event = ControlEvent(kind="pause", value=False)
            await self.result_bus.publish(event)
            logger.info("🎤 Voice command: RESUME")
        
        # Scene description commands
        elif any(word in command for word in ["describe", "what", "see", "scene"]):
            event = ControlEvent(kind="describe_scene", value=None)
            await self.result_bus.publish(event)
            logger.info("🎤 Voice command: DESCRIBE SCENE")
        
        # Quit commands
        elif any(word in command for word in ["quit", "exit", "shutdown"]):
            event = ControlEvent(kind="shutdown", value=None)
            await self.result_bus.publish(event)
            logger.info("🎤 Voice command: QUIT")
        
        else:
            logger.debug(f"Unknown command: {command}")
    
    async def stop(self) -> None:
        """Stop the module."""
        self.running = False
        logger.info(f"{self.name} module stopped")

