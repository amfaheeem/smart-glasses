"""Fusion policy logic."""

from typing import Literal


class FusionPolicy:
    """
    Manages announcement cooldown and prioritization.
    """
    
    def __init__(self):
        # Track last announcement time per track_id
        self.last_announced: dict[int, int] = {}  # track_id -> timestamp_ms
        self.announcement_count = 0
    
    def should_announce(
        self,
        track_id: int,
        timestamp_ms: int,
        urgency: Literal["low", "medium", "high", "critical"],
        stable: bool,
        cooldown_ms: int,
    ) -> bool:
        """
        Determine if an announcement should be made.
        
        Args:
            track_id: Track ID
            timestamp_ms: Current timestamp
            urgency: Urgency level
            stable: Whether track is stable
            cooldown_ms: Cooldown period in milliseconds
        
        Returns:
            True if announcement should be made
        """
        # Always announce critical urgency
        if urgency == "critical":
            return True
        
        # Only announce stable tracks
        if not stable:
            return False
        
        # Check cooldown
        if track_id in self.last_announced:
            elapsed = timestamp_ms - self.last_announced[track_id]
            if elapsed < cooldown_ms:
                return False
        
        return True
    
    def record_announcement(self, track_id: int, timestamp_ms: int) -> None:
        """Record that an announcement was made."""
        self.last_announced[track_id] = timestamp_ms
        self.announcement_count += 1
    
    def get_priority(self, urgency: Literal["low", "medium", "high", "critical"]) -> int:
        """
        Get priority value for an urgency level.
        
        Returns:
            Priority (1=highest, 5=lowest)
        """
        priority_map = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4,
        }
        return priority_map.get(urgency, 5)
    
    def get_announcement_kind(self, label: str) -> Literal["object", "hazard", "navigation", "status"]:
        """
        Determine announcement kind based on label.
        
        Args:
            label: Object label
        
        Returns:
            Announcement kind
        """
        if label in ["hazard", "obstacle"]:
            return "hazard"
        elif label in ["person", "vehicle"]:
            return "object"
        else:
            return "navigation"

