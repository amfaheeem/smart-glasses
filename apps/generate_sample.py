"""Generate sample video and frame directory."""

import argparse
import logging
from pathlib import Path
from sources.sample_generator import generate_sample_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for sample generation."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic sample video and frame directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/samples"),
        help="Output directory (default: data/samples)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Video duration in seconds (default: 10)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second (default: 30)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Frame width (default: 640)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Frame height (default: 480)",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Generating sample data in {args.output}")
    logger.info(f"Duration: {args.duration}s @ {args.fps} FPS")
    logger.info(f"Resolution: {args.width}x{args.height}")
    
    try:
        mp4_path, frames_dir = generate_sample_data(
            output_dir=args.output,
            duration_sec=args.duration,
            fps=args.fps,
            width=args.width,
            height=args.height,
        )
        
        logger.info(f"✓ Successfully generated:")
        logger.info(f"  MP4: {mp4_path}")
        logger.info(f"  Frames: {frames_dir}")
        
    except Exception as e:
        logger.error(f"Failed to generate sample data: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

