"""Stub detector - Generates deterministic detections for demo."""

import logging
from contracts.schemas import Detection

logger = logging.getLogger(__name__)


class StubDetector:
    """
    Deterministic detector for demo purposes.
    
    Generates synthetic detections based on frame_id to ensure
    reproducible behavior without requiring ML models.
    """
    
    def detect(self, frame_id: int, width: int, height: int) -> list[Detection]:
        """
        Generate detections for a frame.
        
        Args:
            frame_id: Frame number
            width: Frame width in pixels
            height: Frame height in pixels
        
        Returns:
            List of Detection objects
        """
        detections = []
        
        # Person moving left to right (appears every 3 frames)
        if frame_id % 3 == 0:
            # Calculate position based on frame_id
            progress = (frame_id * 0.005) % 1.0
            x = 0.05 + progress * 0.7  # Move from left to right
            
            detections.append(Detection(
                label="person",
                confidence=0.85,
                bbox=(x, 0.35, 0.10, 0.25)  # x, y, w, h normalized
            ))
        
        # Door (stationary, always present)
        detections.append(Detection(
            label="door",
            confidence=0.92,
            bbox=(0.75, 0.25, 0.12, 0.40)
        ))
        
        # Obstacle (appears for frames 50-200, grows to simulate approaching)
        if 50 <= frame_id <= 200:
            progress = (frame_id - 50) / 150.0
            size = 0.05 + progress * 0.15  # Grows from 0.05 to 0.20
            
            detections.append(Detection(
                label="obstacle",
                confidence=0.78,
                bbox=(0.40, 0.50, size, size)
            ))
        
        # Second person (enters from right at frame 150)
        if frame_id >= 150:
            progress = (frame_id - 150) * 0.003
            x = 0.85 - progress  # Move from right to left
            
            if x > 0.1:  # Stop before going off screen
                detections.append(Detection(
                    label="person",
                    confidence=0.80,
                    bbox=(x, 0.40, 0.08, 0.20)
                ))
        
        # Hazard (brief appearance frames 200-250)
        if 200 <= frame_id <= 250:
            detections.append(Detection(
                label="hazard",
                confidence=0.75,
                bbox=(0.20, 0.60, 0.12, 0.08)
            ))
        
        return detections

