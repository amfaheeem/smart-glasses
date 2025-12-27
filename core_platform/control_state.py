"""Shared mutable state for system control."""

from dataclasses import dataclass, field
from threading import Lock
from typing import Optional


@dataclass
class ControlState:
    """Shared control state accessible by all modules."""
    
    # Playback control
    paused: bool = False
    speed: float = 1.0  # 0.5, 1.0, 2.0
    pending_seek: Optional[int] = None  # frame_id to seek to
    
    # Module thresholds
    detection_conf_threshold: float = 0.5
    tracker_iou_threshold: float = 0.3
    fusion_cooldown_seconds: float = 3.0
    
    # Internal lock for thread-safe updates
    _lock: Lock = field(default_factory=Lock, repr=False)
    
    def update(self, **kwargs) -> None:
        """Thread-safe update of control state."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def get_snapshot(self) -> dict:
        """Get a snapshot of current state."""
        with self._lock:
            return {
                "paused": self.paused,
                "speed": self.speed,
                "detection_conf_threshold": self.detection_conf_threshold,
                "tracker_iou_threshold": self.tracker_iou_threshold,
                "fusion_cooldown_seconds": self.fusion_cooldown_seconds,
            }

