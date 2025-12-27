"""Camera source - Reads frames from webcam."""

import asyncio
import logging
from typing import Optional
import cv2
from contracts.schemas import FramePacket
from core_platform.frame_bus import FrameBus
from core_platform.clock import Clock
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


class CameraSource:
    """
    Reads frames from laptop webcam.
    
    Supports pause/resume and speed control via ControlState.
    """
    
    def __init__(
        self,
        camera_id: int,
        frame_bus: FrameBus,
        control_state: ControlState,
        fps: int = 15,  # Lower FPS for webcam
        width: int = 640,
        height: int = 480,
    ):
        self.camera_id = camera_id
        self.frame_bus = frame_bus
        self.control_state = control_state
        self.fps = fps
        self.width = width
        self.height = height
        
        self.running = False
        self.current_frame_id = 0
        self.clock: Optional[Clock] = None
    
    async def run(self) -> None:
        """Main loop - read and publish frames from webcam."""
        self.running = True
        
        # Open camera
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            logger.error(f"Failed to open camera {self.camera_id}")
            return
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Get actual resolution
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.clock = Clock(fps=self.fps)
        
        logger.info(
            f"Opened camera {self.camera_id} "
            f"({actual_width}x{actual_height} @ {self.fps} fps)"
        )
        
        try:
            while self.running:
                # Handle pause
                if self.control_state.paused:
                    await asyncio.sleep(0.1)
                    continue
                
                # Read frame
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame {self.current_frame_id}")
                    await asyncio.sleep(0.1)
                    continue
                
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
                
                # Delay based on FPS (ignore speed control for real-time camera)
                delay = 1.0 / self.fps
                await asyncio.sleep(delay)
        
        except Exception as e:
            logger.error(f"Camera error: {e}", exc_info=True)
        finally:
            cap.release()
            logger.info(f"Released camera {self.camera_id}")
    
    async def stop(self) -> None:
        """Stop the camera source."""
        self.running = False

