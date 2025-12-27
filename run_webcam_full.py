#!/usr/bin/env python3
"""Run webcam with scene description and voice (full experience)."""

import asyncio
import logging
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState
from sources.camera_source import CameraSource
from modules.object_detection.module import ObjectDetectionModule
from modules.tracker.module import TrackerModule
from modules.navigation.module import NavigationModule
from modules.fusion.module import FusionModule
from modules.scene_description.module import SceneDescriptionModule
from modules.voice_input.module import VoiceInputModule
from modules.voice_output.module import VoiceOutputModule
from contracts.schemas import FusionAnnouncement, SceneDescription

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run the full pipeline with all features."""
    camera_id = 0
    fps = 15
    
    logger.info("=" * 70)
    logger.info("SMART GLASSES - FULL EXPERIENCE")
    logger.info("=" * 70)
    logger.info("Features:")
    logger.info("  ✓ Real-time object detection (YOLO)")
    logger.info("  ✓ Object tracking")
    logger.info("  ✓ Navigation guidance")
    logger.info("  ✓ Scene descriptions (every 5s)")
    logger.info("  ✓ Voice commands (pause, resume, describe, quit)")
    logger.info("  ✓ Voice output (TTS announcements)")
    logger.info("")
    logger.info("Voice commands you can say:")
    logger.info("  • 'pause' or 'stop' - Pause processing")
    logger.info("  • 'resume' or 'play' - Resume processing")
    logger.info("  • 'describe' or 'what do you see' - Describe scene now")
    logger.info("  • 'quit' or 'exit' - Stop the system")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 70)
    logger.info("")
    
    # Create shared components
    control_state = ControlState()
    frame_bus = FrameBus()
    result_bus = ResultBus()
    
    # Create camera source
    camera_source = CameraSource(
        camera_id=camera_id,
        frame_bus=frame_bus,
        control_state=control_state,
        fps=fps,
        width=640,
        height=480,
    )
    
    # Create ALL modules (including new ones!)
    modules = [
        ObjectDetectionModule(use_yolo=True),  # Real YOLO detection
        TrackerModule(),
        NavigationModule(),
        FusionModule(),
        SceneDescriptionModule(description_interval=5.0),  # NEW!
        VoiceInputModule(enabled=True, language="en-US"),  # NEW!
        VoiceOutputModule(enabled=True, rate=175),  # NEW!
    ]
    
    # Start all
    tasks = []
    tasks.append(asyncio.create_task(camera_source.run()))
    
    for module in modules:
        module_tasks = await module.start(frame_bus, result_bus, control_state)
        tasks.extend(module_tasks)
    
    logger.info("✓ All modules started")
    logger.info("")
    logger.info("=" * 70)
    logger.info("LIVE OUTPUT:")
    logger.info("=" * 70)
    
    # Log events for visibility
    async def log_events():
        """Log announcements and descriptions."""
        async for event in result_bus.subscribe_all():
            if isinstance(event, FusionAnnouncement):
                logger.info(f"📢 ANNOUNCEMENT: {event.text}")
            elif isinstance(event, SceneDescription):
                logger.info(f"🖼️  SCENE: {event.description}")
    
    tasks.append(asyncio.create_task(log_events()))
    
    try:
        # Wait for all tasks
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down...")
    finally:
        # Stop camera source
        await camera_source.stop()
        
        # Stop modules
        for module in modules:
            await module.stop()
        
        # Shutdown buses
        await frame_bus.shutdown()
        await result_bus.shutdown()
        
        # Cancel tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    logger.info("Done!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")

