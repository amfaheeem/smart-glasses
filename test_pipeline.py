#!/usr/bin/env python3
"""Simple run script for testing - runs just the pipeline without UI."""

import asyncio
import logging
from pathlib import Path
import signal

from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState
from sources.video_source import VideoSource
from modules.object_detection.module import ObjectDetectionModule
from modules.tracker.module import TrackerModule
from modules.navigation.module import NavigationModule
from modules.fusion.module import FusionModule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run the pipeline without UI."""
    video_path = Path("data/samples/sample.mp4")
    
    if not video_path.exists():
        logger.error(f"Video not found: {video_path}")
        logger.error("Run: python -m apps.generate_sample first")
        return
    
    # Create shared components
    control_state = ControlState()
    frame_bus = FrameBus()
    result_bus = ResultBus()
    
    # Create video source
    video_source = VideoSource(video_path, frame_bus, control_state)
    
    # Create modules
    modules = [
        ObjectDetectionModule(),
        TrackerModule(),
        NavigationModule(),
        FusionModule(),
    ]
    
    # Start all
    tasks = []
    tasks.append(asyncio.create_task(video_source.run()))
    
    for module in modules:
        module_tasks = await module.start(frame_bus, result_bus, control_state)
        tasks.extend(module_tasks)
    
    logger.info("Pipeline started - processing video...")
    logger.info("Press Ctrl+C to stop")
    
    # Subscribe to announcements and print them
    async def print_announcements():
        from contracts.schemas import FusionAnnouncement
        async for announcement in result_bus.subscribe_type(FusionAnnouncement):
            logger.info(f"📢 ANNOUNCEMENT: {announcement.text}")
    
    tasks.append(asyncio.create_task(print_announcements()))
    
    try:
        # Wait for all tasks
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Stop video source
        await video_source.stop()
        
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
    asyncio.run(main())

