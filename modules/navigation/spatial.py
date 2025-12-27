"""Spatial analysis utilities."""

from typing import Literal


def analyze_direction(bbox: tuple[float, float, float, float]) -> Literal["left", "center", "right"]:
    """
    Determine horizontal direction based on bbox center.
    
    Args:
        bbox: (x, y, w, h) in normalized coordinates
    
    Returns:
        "left", "center", or "right"
    """
    x, y, w, h = bbox
    center_x = x + w / 2
    
    if center_x < 0.33:
        return "left"
    elif center_x < 0.66:
        return "center"
    else:
        return "right"


def analyze_zone(bbox: tuple[float, float, float, float]) -> Literal["near", "mid", "far"]:
    """
    Determine distance zone based on bbox area (proxy for distance).
    
    Args:
        bbox: (x, y, w, h) in normalized coordinates
    
    Returns:
        "near", "mid", or "far"
    """
    x, y, w, h = bbox
    area = w * h
    
    if area > 0.15:
        return "near"
    elif area > 0.05:
        return "mid"
    else:
        return "far"


def analyze_movement(
    current_bbox: tuple[float, float, float, float],
    history: list[dict],
) -> Literal["approaching", "receding", "stationary"]:
    """
    Determine movement pattern based on bbox size change.
    
    Args:
        current_bbox: Current bbox
        history: List of historical track data
    
    Returns:
        "approaching", "receding", or "stationary"
    """
    if len(history) < 2:
        return "stationary"
    
    prev_bbox = history[-2]["bbox"]
    
    current_area = current_bbox[2] * current_bbox[3]
    prev_area = prev_bbox[2] * prev_bbox[3]
    
    # Growing = approaching, shrinking = receding
    if current_area > prev_area * 1.05:
        return "approaching"
    elif current_area < prev_area * 0.95:
        return "receding"
    else:
        return "stationary"


def compute_urgency(
    zone: Literal["near", "mid", "far"],
    movement: Literal["approaching", "receding", "stationary"],
) -> Literal["low", "medium", "high", "critical"]:
    """
    Compute urgency level based on zone and movement.
    
    Returns:
        "low", "medium", "high", or "critical"
    """
    if zone == "near" and movement == "approaching":
        return "critical"
    elif zone == "near":
        return "high"
    elif zone == "mid" and movement == "approaching":
        return "medium"
    else:
        return "low"

