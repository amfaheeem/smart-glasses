"""Clock helper for timestamp calculations."""

import time


class Clock:
    """Helper for managing timestamps with speed control."""
    
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.frame_duration_ms = 1000 / fps
        self.start_time_ms = int(time.time() * 1000)
    
    def frame_to_timestamp(self, frame_id: int) -> int:
        """Convert frame ID to timestamp in milliseconds."""
        return self.start_time_ms + int(frame_id * self.frame_duration_ms)
    
    def get_frame_delay(self, speed: float) -> float:
        """Get delay in seconds between frames at given speed."""
        if speed <= 0:
            speed = 1.0
        return (1.0 / self.fps) / speed
    
    @staticmethod
    def now_ms() -> int:
        """Get current timestamp in milliseconds."""
        return int(time.time() * 1000)

