"""Video source - Reads frames from MP4 or frame directory."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
import cv2
from contracts.schemas import FramePacket
from core_platform.frame_bus import FrameBus
from core_platform.clock import Clock
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


class VideoSource:
    """
    Reads frames from MP4 file or frame directory.
    
    Supports pause/resume and speed control via ControlState.
    """
    
    def __init__(
        self,
        source: Path,
        frame_bus: FrameBus,
        control_state: ControlState,
    ):
        self.source = Path(source)
        self.frame_bus = frame_bus
        self.control_state = control_state
        
        # Determine source type
        if self.source.suffix == ".mp4":
            self.source_type = "mp4"
        elif self.source.is_dir():
            self.source_type = "frames"
        else:
            raise ValueError(f"Unknown source type: {self.source}")
        
        self.running = False
        self.current_frame_id = 0
        self.total_frames = 0
        self.fps = 30
        self.clock: Optional[Clock] = None
    
    async def run(self) -> None:
        """Main loop - read and publish frames."""
        self.running = True
        
        if self.source_type == "mp4":
            await self._run_mp4()
        else:
            await self._run_frames()
        
        logger.info("VideoSource finished")
    
    async def _run_mp4(self) -> None:
        """Read from MP4 file."""
        cap = cv2.VideoCapture(str(self.source))
        
        if not cap.isOpened():
            logger.error(f"Failed to open video: {self.source}")
            return
        
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        self.clock = Clock(fps=self.fps)
        
        logger.info(
            f"Opened MP4: {self.source} "
            f"({self.total_frames} frames @ {self.fps} fps)"
        )
        
        try:
            while self.running and self.current_frame_id < self.total_frames:
                # Handle pause
                if self.control_state.paused:
                    await asyncio.sleep(0.1)
                    continue
                
                # Handle seek
                if self.control_state.pending_seek is not None:
                    seek_frame = self.control_state.pending_seek
                    self.control_state.pending_seek = None
                    cap.set(cv2.CAP_PROP_POS_FRAMES, seek_frame)
                    self.current_frame_id = seek_frame
                    logger.info(f"Seeked to frame {seek_frame}")
                    continue
                
                # Read frame
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame {self.current_frame_id}")
                    break
                
                # Encode as JPEG
                _, jpg_buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                jpg_bytes = jpg_buffer.tobytes()
                
                # Create packet
                height, width = frame.shape[:2]
                packet = FramePacket(
                    frame_id=self.current_frame_id,
                    timestamp_ms=self.clock.frame_to_timestamp(self.current_frame_id),
                    width=width,
                    height=height,
                    jpg_bytes=jpg_bytes,
                )
                
                # Publish
                await self.frame_bus.publish(packet)
                
                self.current_frame_id += 1
                
                # Delay based on speed
                delay = self.clock.get_frame_delay(self.control_state.speed)
                await asyncio.sleep(delay)
        
        finally:
            cap.release()
    
    async def _run_frames(self) -> None:
        """Read from frame directory."""
        # Load metadata
        metadata_path = self.source / "metadata.json"
        if not metadata_path.exists():
            logger.error(f"metadata.json not found in {self.source}")
            return
        
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        self.total_frames = metadata["total_frames"]
        self.fps = metadata["fps"]
        self.clock = Clock(fps=self.fps)
        
        logger.info(
            f"Opened frame directory: {self.source} "
            f"({self.total_frames} frames @ {self.fps} fps)"
        )
        
        try:
            while self.running and self.current_frame_id < self.total_frames:
                # Handle pause
                if self.control_state.paused:
                    await asyncio.sleep(0.1)
                    continue
                
                # Handle seek
                if self.control_state.pending_seek is not None:
                    self.current_frame_id = self.control_state.pending_seek
                    self.control_state.pending_seek = None
                    logger.info(f"Seeked to frame {self.current_frame_id}")
                    continue
                
                # Read JPEG file
                frame_path = self.source / f"frame_{self.current_frame_id:04d}.jpg"
                
                if not frame_path.exists():
                    logger.warning(f"Frame file not found: {frame_path}")
                    break
                
                with open(frame_path, 'rb') as f:
                    jpg_bytes = f.read()
                
                # Create packet
                packet = FramePacket(
                    frame_id=self.current_frame_id,
                    timestamp_ms=self.clock.frame_to_timestamp(self.current_frame_id),
                    width=metadata["width"],
                    height=metadata["height"],
                    jpg_bytes=jpg_bytes,
                )
                
                # Publish
                await self.frame_bus.publish(packet)
                
                self.current_frame_id += 1
                
                # Delay based on speed
                delay = self.clock.get_frame_delay(self.control_state.speed)
                await asyncio.sleep(delay)
        
        except Exception as e:
            logger.error(f"Error reading frames: {e}")
    
    async def stop(self) -> None:
        """Stop the video source."""
        self.running = False

