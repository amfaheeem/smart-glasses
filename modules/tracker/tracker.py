"""Track state management."""

from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Track:
    """State for a single tracked object."""
    
    track_id: int
    label: str
    bbox: tuple[float, float, float, float]
    
    # History
    history: deque = field(default_factory=lambda: deque(maxlen=5))
    
    # Stability
    consecutive_hits: int = 0
    frames_since_update: int = 0
    
    # State
    stable: bool = False
    
    def update(
        self,
        bbox: tuple[float, float, float, float],
        frame_id: int,
        timestamp_ms: int,
    ) -> None:
        """Update track with new detection."""
        self.bbox = bbox
        self.history.append({
            "bbox": bbox,
            "frame_id": frame_id,
            "timestamp_ms": timestamp_ms,
        })
        
        self.consecutive_hits += 1
        self.frames_since_update = 0
        
        # Mark as stable after N consecutive hits
        if self.consecutive_hits >= 3:
            self.stable = True
    
    def mark_missed(self) -> None:
        """Mark track as missed in current frame."""
        self.frames_since_update += 1
        self.consecutive_hits = 0
    
    def compute_velocity(self) -> Optional[tuple[float, float]]:
        """Compute velocity from history."""
        if len(self.history) < 2:
            return None
        
        recent = self.history[-1]
        prev = self.history[-2]
        
        # Use center points
        rx, ry, rw, rh = recent["bbox"]
        px, py, pw, ph = prev["bbox"]
        
        rcx, rcy = rx + rw/2, ry + rh/2
        pcx, pcy = px + pw/2, py + ph/2
        
        dx = rcx - pcx
        dy = rcy - pcy
        
        return (dx, dy)


class Tracker:
    """Multi-object tracker using IoU matching."""
    
    def __init__(self, max_age: int = 30):
        self.max_age = max_age  # Frames before track eviction
        self.next_track_id = 1
        self.tracks: dict[int, Track] = {}
    
    def get_track(self, track_id: int) -> Optional[Track]:
        """Get track by ID."""
        return self.tracks.get(track_id)
    
    def create_track(
        self,
        label: str,
        bbox: tuple[float, float, float, float],
        frame_id: int,
        timestamp_ms: int,
    ) -> Track:
        """Create a new track."""
        track = Track(
            track_id=self.next_track_id,
            label=label,
            bbox=bbox,
        )
        track.update(bbox, frame_id, timestamp_ms)
        
        self.tracks[track.track_id] = track
        self.next_track_id += 1
        
        return track
    
    def update_track(
        self,
        track_id: int,
        bbox: tuple[float, float, float, float],
        frame_id: int,
        timestamp_ms: int,
    ) -> Track:
        """Update existing track."""
        track = self.tracks[track_id]
        track.update(bbox, frame_id, timestamp_ms)
        return track
    
    def mark_missed_tracks(self, matched_track_ids: set[int]) -> None:
        """Mark tracks that were not matched."""
        for track_id, track in list(self.tracks.items()):
            if track_id not in matched_track_ids:
                track.mark_missed()
    
    def evict_old_tracks(self) -> list[int]:
        """Remove tracks that haven't been seen for max_age frames."""
        evicted = []
        for track_id, track in list(self.tracks.items()):
            if track.frames_since_update > self.max_age:
                del self.tracks[track_id]
                evicted.append(track_id)
        
        return evicted
    
    def get_active_tracks(self) -> dict[int, tuple[float, float, float, float]]:
        """Get current bboxes for all active tracks."""
        return {
            track_id: track.bbox
            for track_id, track in self.tracks.items()
        }

