"""Tests for navigation module."""

import pytest
from modules.navigation.spatial import (
    analyze_direction,
    analyze_zone,
    analyze_movement,
    compute_urgency,
)
from modules.navigation.guidance import generate_guidance_text


def test_analyze_direction_left():
    """Test direction analysis - left."""
    bbox = (0.1, 0.3, 0.1, 0.1)  # Center at 0.15 (< 0.33 = left)
    direction = analyze_direction(bbox)
    assert direction == "left"


def test_analyze_direction_center():
    """Test direction analysis - center."""
    bbox = (0.4, 0.3, 0.1, 0.1)  # Center at 0.45 (between 0.33 and 0.66)
    direction = analyze_direction(bbox)
    assert direction == "center"


def test_analyze_direction_right():
    """Test direction analysis - right."""
    bbox = (0.7, 0.3, 0.1, 0.1)  # Center at 0.75 (> 0.66)
    direction = analyze_direction(bbox)
    assert direction == "right"


def test_analyze_zone_near():
    """Test zone analysis - near."""
    bbox = (0.3, 0.3, 0.4, 0.4)  # Area = 0.16 (> 0.15 = near)
    zone = analyze_zone(bbox)
    assert zone == "near"


def test_analyze_zone_mid():
    """Test zone analysis - mid."""
    bbox = (0.3, 0.3, 0.2, 0.3)  # Area = 0.06 (between 0.05 and 0.15)
    zone = analyze_zone(bbox)
    assert zone == "mid"


def test_analyze_zone_far():
    """Test zone analysis - far."""
    bbox = (0.4, 0.4, 0.1, 0.1)  # Area = 0.01 (< 0.05)
    zone = analyze_zone(bbox)
    assert zone == "far"


def test_analyze_movement_approaching():
    """Test movement analysis - approaching."""
    current_bbox = (0.3, 0.3, 0.2, 0.2)  # Area = 0.04
    history = [
        {"bbox": (0.3, 0.3, 0.15, 0.15)},  # Area = 0.0225 (smaller)
        {"bbox": (0.3, 0.3, 0.18, 0.18)},  # Area = 0.0324
    ]
    
    movement = analyze_movement(current_bbox, history)
    assert movement == "approaching"


def test_analyze_movement_receding():
    """Test movement analysis - receding."""
    current_bbox = (0.3, 0.3, 0.1, 0.1)  # Area = 0.01
    history = [
        {"bbox": (0.3, 0.3, 0.2, 0.2)},  # Area = 0.04 (larger)
        {"bbox": (0.3, 0.3, 0.15, 0.15)},  # Area = 0.0225
    ]
    
    movement = analyze_movement(current_bbox, history)
    assert movement == "receding"


def test_analyze_movement_stationary():
    """Test movement analysis - stationary."""
    current_bbox = (0.3, 0.3, 0.1, 0.1)
    history = [
        {"bbox": (0.3, 0.3, 0.1, 0.1)},
        {"bbox": (0.3, 0.3, 0.1, 0.1)},
    ]
    
    movement = analyze_movement(current_bbox, history)
    assert movement == "stationary"


def test_compute_urgency_critical():
    """Test urgency computation - critical."""
    urgency = compute_urgency("near", "approaching")
    assert urgency == "critical"


def test_compute_urgency_high():
    """Test urgency computation - high."""
    urgency = compute_urgency("near", "stationary")
    assert urgency == "high"


def test_compute_urgency_medium():
    """Test urgency computation - medium."""
    urgency = compute_urgency("mid", "approaching")
    assert urgency == "medium"


def test_compute_urgency_low():
    """Test urgency computation - low."""
    urgency = compute_urgency("far", "stationary")
    assert urgency == "low"


def test_generate_guidance_text_critical():
    """Test guidance text generation - critical situation."""
    text = generate_guidance_text(
        label="person",
        direction="left",
        zone="near",
        movement="approaching",
    )
    assert "person" in text.lower()
    assert "close" in text.lower()


def test_generate_guidance_text_approaching():
    """Test guidance text generation - approaching."""
    text = generate_guidance_text(
        label="obstacle",
        direction="center",
        zone="mid",
        movement="approaching",
    )
    assert "obstacle" in text.lower()
    assert "approach" in text.lower()


def test_generate_guidance_text_stationary():
    """Test guidance text generation - stationary."""
    text = generate_guidance_text(
        label="door",
        direction="right",
        zone="mid",
        movement="stationary",
    )
    assert "door" in text.lower()
    assert "right" in text.lower()

