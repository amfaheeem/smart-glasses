#!/usr/bin/env python3
"""Run the smart glasses pipeline with live webcam input."""

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
from modules.scene_description.module import SceneDescriptionModule  # NEW!
from contracts.schemas import FusionAnnouncement, NavigationGuidance, SceneDescription  # NEW!

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run the pipeline with webcam."""
    # Camera settings
    camera_id = 0  # Default webcam
    fps = 15  # Lower FPS for real-time processing
    
    logger.info("Starting Smart Glasses with Webcam...")
    logger.info(f"Camera ID: {camera_id}, FPS: {fps}")
    logger.info("Press Ctrl+C to stop")
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
    
    # Create modules
    modules = [
        ObjectDetectionModule(),
        TrackerModule(),
        NavigationModule(),
        FusionModule(),
        SceneDescriptionModule(description_interval=5.0),  # NEW! Scene descriptions every 5s
    ]
    
    # Start all
    tasks = []
    tasks.append(asyncio.create_task(camera_source.run()))
    
    for module in modules:
        module_tasks = await module.start(frame_bus, result_bus, control_state)
        tasks.extend(module_tasks)
    
    logger.info("✓ All modules started")
    logger.info("")
    logger.info("=" * 60)
    logger.info("ANNOUNCEMENTS:")
    logger.info("=" * 60)
    
    # Subscribe to announcements and navigation guidance
    async def print_events():
        """Print navigation guidance and announcements."""
        async for event in result_bus.subscribe_all():
            if isinstance(event, FusionAnnouncement):
                logger.info(f"📢 {event.text.upper()} [{event.kind}]")
            elif isinstance(event, SceneDescription):  # NEW!
                logger.info(f"🖼️  SCENE: {event.description}")
            elif isinstance(event, NavigationGuidance):
                urgency_emoji = {
                    "low": "ℹ️",
                    "medium": "⚠️",
                    "high": "⚠️⚠️",
                    "critical": "🚨",
                }
                emoji = urgency_emoji.get(event.urgency, "•")
                logger.info(
                    f"{emoji} Track #{event.track_id}: {event.guidance_text} "
                    f"[{event.direction}, {event.zone}, {event.movement}]"
                )
    
    tasks.append(asyncio.create_task(print_events()))
    
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

