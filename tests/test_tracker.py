"""Tests for tracker module."""

import pytest
from modules.tracker.matching import compute_iou, match_detections_to_tracks
from modules.tracker.tracker import Tracker


def test_compute_iou_overlap():
    """Test IoU computation for overlapping boxes."""
    bbox1 = (0.1, 0.1, 0.2, 0.2)  # x, y, w, h
    bbox2 = (0.15, 0.15, 0.2, 0.2)  # Overlaps with bbox1
    
    iou = compute_iou(bbox1, bbox2)
    
    assert 0 < iou < 1  # Should have some overlap
    assert iou > 0.3  # Reasonable overlap


def test_compute_iou_no_overlap():
    """Test IoU computation for non-overlapping boxes."""
    bbox1 = (0.1, 0.1, 0.1, 0.1)
    bbox2 = (0.5, 0.5, 0.1, 0.1)  # Far away
    
    iou = compute_iou(bbox1, bbox2)
    
    assert iou == 0.0


def test_compute_iou_identical():
    """Test IoU computation for identical boxes."""
    bbox1 = (0.1, 0.1, 0.2, 0.2)
    bbox2 = (0.1, 0.1, 0.2, 0.2)
    
    iou = compute_iou(bbox1, bbox2)
    
    assert abs(iou - 1.0) < 0.0001  # Allow for floating-point precision


def test_match_detections_to_tracks():
    """Test detection-to-track matching."""
    detections = [
        (0, (0.1, 0.1, 0.1, 0.1)),
        (1, (0.5, 0.5, 0.1, 0.1)),
    ]
    
    tracks = {
        1: (0.12, 0.12, 0.1, 0.1),  # Should match detection 0
        2: (0.52, 0.52, 0.1, 0.1),  # Should match detection 1
    }
    
    matches, unmatched_dets, unmatched_tracks = match_detections_to_tracks(
        detections, tracks, iou_threshold=0.3
    )
    
    assert len(matches) == 2
    assert 0 in matches  # Detection 0 matched
    assert 1 in matches  # Detection 1 matched
    assert len(unmatched_dets) == 0
    assert len(unmatched_tracks) == 0


def test_tracker_create_track():
    """Test track creation."""
    tracker = Tracker()
    
    track = tracker.create_track(
        label="person",
        bbox=(0.1, 0.1, 0.1, 0.1),
        frame_id=0,
        timestamp_ms=0,
    )
    
    assert track.track_id == 1
    assert track.label == "person"
    assert track.bbox == (0.1, 0.1, 0.1, 0.1)
    assert not track.stable  # Not stable yet (needs consecutive hits)


def test_tracker_update_track():
    """Test track update and stability."""
    tracker = Tracker()
    
    # Create track
    track = tracker.create_track(
        label="person",
        bbox=(0.1, 0.1, 0.1, 0.1),
        frame_id=0,
        timestamp_ms=0,
    )
    
    # Update track multiple times to make it stable
    for i in range(1, 4):
        tracker.update_track(
            track.track_id,
            bbox=(0.1 + i * 0.01, 0.1, 0.1, 0.1),  # Slightly moved
            frame_id=i,
            timestamp_ms=i * 33,
        )
    
    track = tracker.get_track(1)
    assert track.stable  # Should be stable after 3 consecutive updates


def test_tracker_eviction():
    """Test track eviction after max_age."""
    tracker = Tracker(max_age=5)
    
    # Create track
    track = tracker.create_track(
        label="person",
        bbox=(0.1, 0.1, 0.1, 0.1),
        frame_id=0,
        timestamp_ms=0,
    )
    
    track_id = track.track_id
    
    # Mark as missed multiple times
    for _ in range(6):
        tracker.mark_missed_tracks(set())
    
    # Evict old tracks
    evicted = tracker.evict_old_tracks()
    
    assert track_id in evicted
    assert tracker.get_track(track_id) is None


def test_tracker_velocity_computation():
    """Test velocity computation from track history."""
    tracker = Tracker()
    
    # Create track
    track = tracker.create_track(
        label="person",
        bbox=(0.1, 0.1, 0.1, 0.1),
        frame_id=0,
        timestamp_ms=0,
    )
    
    # Update with moved bbox
    tracker.update_track(
        track.track_id,
        bbox=(0.15, 0.12, 0.1, 0.1),  # Moved right and down
        frame_id=1,
        timestamp_ms=33,
    )
    
    track = tracker.get_track(track.track_id)
    velocity = track.compute_velocity()
    
    assert velocity is not None
    assert velocity[0] > 0  # Moving right
    assert velocity[1] > 0  # Moving down

