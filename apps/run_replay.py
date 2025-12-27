"""Run the smart glasses pipeline in replay mode."""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path
import uvicorn

from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState
from sources.video_source import VideoSource
from sources.sample_generator import generate_sample_data
from modules.object_detection.module import ObjectDetectionModule
from modules.tracker.module import TrackerModule
from modules.navigation.module import NavigationModule
from modules.fusion.module import FusionModule
from ui.server import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ReplaySystem:
    """Orchestrates the replay system."""
    
    def __init__(
        self,
        video_path: Path,
        host: str,
        port: int,
    ):
        self.video_path = Path(video_path)
        self.host = host
        self.port = port
        
        # Create shared components
        self.control_state = ControlState()
        self.frame_bus = FrameBus()
        self.result_bus = ResultBus()
        
        # Create video source
        self.video_source = VideoSource(
            self.video_path,
            self.frame_bus,
            self.control_state,
        )
        
        # Create modules
        self.modules = [
            ObjectDetectionModule(),
            TrackerModule(),
            NavigationModule(),
            FusionModule(),
        ]
        
        # Create UI app
        self.app = create_app(
            self.frame_bus,
            self.result_bus,
            self.control_state,
        )
        
        # Track tasks
        self.tasks = []
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start all components."""
        logger.info("Starting Smart Glasses Replay System")
        
        # Start video source
        video_task = asyncio.create_task(self.video_source.run())
        self.tasks.append(video_task)
        
        # Start modules
        for module in self.modules:
            module_tasks = await module.start(
                self.frame_bus,
                self.result_bus,
                self.control_state,
            )
            self.tasks.extend(module_tasks)
        
        # Start UI server in a separate task
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        server_task = asyncio.create_task(server.serve())
        self.tasks.append(server_task)
        
        logger.info(f"✓ System started - UI available at http://{self.host}:{self.port}")
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        
        # Cleanup
        await self.stop()
    
    async def stop(self):
        """Stop all components."""
        logger.info("Shutting down...")
        
        # Stop video source
        await self.video_source.stop()
        
        # Stop modules
        for module in self.modules:
            await module.stop()
        
        # Shutdown buses
        await self.frame_bus.shutdown()
        await self.result_bus.shutdown()
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("✓ Shutdown complete")
    
    def signal_handler(self, sig):
        """Handle shutdown signal."""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        self.shutdown_event.set()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Glasses Navigation Pipeline - Replay Mode"
    )
    parser.add_argument(
        "--video",
        type=Path,
        default=Path("data/samples/sample.mp4"),
        help="Path to video file or frame directory (default: data/samples/sample.mp4)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for web UI (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for web UI (default: 8000)",
    )
    parser.add_argument(
        "--auto-generate",
        action="store_true",
        default=True,
        help="Auto-generate sample video if not found (default: True)",
    )
    parser.add_argument(
        "--no-auto-generate",
        dest="auto_generate",
        action="store_false",
        help="Disable auto-generation of sample video",
    )
    
    args = parser.parse_args()
    
    # Check if video exists
    if not args.video.exists() and args.auto_generate:
        logger.info(f"Video not found: {args.video}")
        logger.info("Auto-generating sample video...")
        
        try:
            output_dir = args.video.parent
            generate_sample_data(output_dir)
            logger.info(f"✓ Sample video generated at {args.video}")
        except Exception as e:
            logger.error(f"Failed to generate sample video: {e}", exc_info=True)
            return 1
    
    if not args.video.exists():
        logger.error(f"Video not found: {args.video}")
        logger.error("Use --auto-generate or run: python -m apps.generate_sample")
        return 1
    
    # Create system
    system = ReplaySystem(
        video_path=args.video,
        host=args.host,
        port=args.port,
    )
    
    # Run system with asyncio.run
    try:
        asyncio.run(system.start())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

