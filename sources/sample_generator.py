"""Sample video and frame directory generator."""

import json
import logging
from pathlib import Path
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def generate_sample_data(
    output_dir: Path,
    duration_sec: int = 10,
    fps: int = 30,
    width: int = 640,
    height: int = 480,
) -> tuple[Path, Path]:
    """
    Generate synthetic video with moving shapes for testing.
    
    Creates:
    - output_dir/sample.mp4
    - output_dir/sample_frames/ with individual JPEGs and metadata.json
    
    Returns:
        (mp4_path, frames_dir_path)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    mp4_path = output_dir / "sample.mp4"
    frames_dir = output_dir / "sample_frames"
    frames_dir.mkdir(exist_ok=True)
    
    total_frames = duration_sec * fps
    
    # Define actors - synthetic objects that move
    actors = [
        {
            "label": "person",
            "shape": "rect",
            "color": (200, 100, 100),  # BGR: Blue-ish
            "start_pos": (50, 200),
            "velocity": (3, 0.5),
            "size": (60, 120),
            "frames": f"0-{total_frames-1}",
        },
        {
            "label": "door",
            "shape": "rect",
            "color": (100, 200, 100),  # Green-ish
            "start_pos": (500, 150),
            "velocity": (0, 0),  # Stationary
            "size": (80, 180),
            "frames": f"0-{total_frames-1}",
        },
        {
            "label": "obstacle",
            "shape": "circle",
            "color": (100, 100, 200),  # Red-ish
            "start_pos": (300, 350),
            "velocity": (-2, -1),
            "size": (30, 30),  # Will grow to simulate approaching
            "frames": f"0-{min(200, total_frames-1)}",
        },
        {
            "label": "person",
            "shape": "rect",
            "color": (200, 200, 100),  # Cyan-ish
            "start_pos": (580, 250),
            "velocity": (-2.5, 0),
            "size": (50, 100),
            "frames": f"150-{total_frames-1}",
        },
    ]
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(str(mp4_path), fourcc, fps, (width, height))
    
    logger.info(f"Generating {total_frames} frames...")
    
    for frame_idx in range(total_frames):
        # Create gray background
        frame = np.full((height, width, 3), 128, dtype=np.uint8)
        
        for actor in actors:
            # Check if actor is active in this frame
            frame_range = actor["frames"].split("-")
            start_frame = int(frame_range[0])
            end_frame = int(frame_range[1])
            
            if not (start_frame <= frame_idx <= end_frame):
                continue
            
            # Calculate position with wrapping
            elapsed = frame_idx - start_frame
            x = (actor["start_pos"][0] + actor["velocity"][0] * elapsed) % width
            y = (actor["start_pos"][1] + actor["velocity"][1] * elapsed) % height
            
            # For obstacle, simulate approaching by growing size
            if actor["label"] == "obstacle" and actor["shape"] == "circle":
                growth_factor = 1.0 + (elapsed / 200.0) * 1.5
                size = int(actor["size"][0] * growth_factor)
            else:
                size = actor["size"]
            
            # Draw shape
            if actor["shape"] == "rect":
                pt1 = (int(x), int(y))
                pt2 = (int(x + size[0]), int(y + size[1]))
                cv2.rectangle(frame, pt1, pt2, actor["color"], -1)
                # Add border
                cv2.rectangle(frame, pt1, pt2, (255, 255, 255), 2)
            elif actor["shape"] == "circle":
                center = (int(x), int(y))
                cv2.circle(frame, center, size, actor["color"], -1)
                cv2.circle(frame, center, size, (255, 255, 255), 2)
            
            # Add label text
            text_pos = (int(x), int(y) - 10)
            cv2.putText(
                frame, 
                actor["label"], 
                text_pos, 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (255, 255, 255), 
                1
            )
        
        # Write to video
        video_writer.write(frame)
        
        # Save as individual JPEG
        frame_filename = frames_dir / f"frame_{frame_idx:04d}.jpg"
        cv2.imwrite(str(frame_filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    video_writer.release()
    
    # Write metadata for frame directory
    metadata = {
        "fps": fps,
        "width": width,
        "height": height,
        "total_frames": total_frames,
        "duration_sec": duration_sec,
        "actors": actors,
    }
    
    metadata_path = frames_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Generated MP4: {mp4_path}")
    logger.info(f"Generated frame directory: {frames_dir}")
    logger.info(f"  - {total_frames} frames")
    logger.info(f"  - metadata.json")
    
    return mp4_path, frames_dir

