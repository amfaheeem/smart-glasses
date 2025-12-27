"""Guidance text generation."""

from typing import Literal


def generate_guidance_text(
    label: str,
    direction: Literal["left", "center", "right"],
    zone: Literal["near", "mid", "far"],
    movement: Literal["approaching", "receding", "stationary"],
) -> str:
    """
    Generate natural language guidance text.
    
    Args:
        label: Object label
        direction: Horizontal direction
        zone: Distance zone
        movement: Movement pattern
    
    Returns:
        Guidance text string
    """
    # Critical situations
    if zone == "near" and movement == "approaching":
        return f"{label} very close, {direction}"
    
    # Approaching objects
    if movement == "approaching":
        if zone == "mid":
            return f"{label} approaching on {direction}"
        else:  # far
            return f"{label} detected {direction}"
    
    # Stationary objects
    if movement == "stationary":
        if zone == "near":
            return f"{label} nearby on {direction}"
        elif zone == "mid":
            return f"{label} ahead on {direction}"
        else:
            return f"{label} {direction}"
    
    # Receding objects
    if movement == "receding":
        return f"{label} moving away"
    
    # Fallback
    return f"{label} {direction}"

