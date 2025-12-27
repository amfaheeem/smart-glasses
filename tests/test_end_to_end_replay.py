"""End-to-end replay tests."""

import pytest
import asyncio
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState
from contracts.schemas import (
    FramePacket,
    DetectionResult,
    TrackUpdate,
    NavigationGuidance,
    FusionAnnouncement,
)
from modules.object_detection.module import ObjectDetectionModule
from modules.tracker.module import TrackerModule
from modules.navigation.module import NavigationModule
from modules.fusion.module import FusionModule


@pytest.mark.asyncio
async def test_full_pipeline():
    """Test full pipeline with synthetic frames."""
    # Setup
    control_state = ControlState()
    frame_bus = FrameBus()
    result_bus = ResultBus()
    
    # Collect events by type
    detections = []
    tracks = []
    guidances = []
    announcements = []
    
    async def event_collector():
        async for event in result_bus.subscribe_all():
            if isinstance(event, DetectionResult):
                detections.append(event)
            elif isinstance(event, TrackUpdate):
                tracks.append(event)
            elif isinstance(event, NavigationGuidance):
                guidances.append(event)
            elif isinstance(event, FusionAnnouncement):
                announcements.append(event)
            
            # Stop after collecting enough events
            if (len(detections) >= 10 and len(tracks) >= 5 and
                len(guidances) >= 5 and len(announcements) >= 1):
                break
    
    collector_task = asyncio.create_task(event_collector())
    
    # Start modules
    modules = [
        ObjectDetectionModule(),
        TrackerModule(),
        NavigationModule(),
        FusionModule(),
    ]
    
    tasks = []
    for module in modules:
        module_tasks = await module.start(frame_bus, result_bus, control_state)
        tasks.extend(module_tasks)
    
    # Give modules time to start
    await asyncio.sleep(0.1)
    
    # Publish synthetic frames
    for i in range(50):
        frame = FramePacket(
            frame_id=i,
            timestamp_ms=i * 33,
            width=640,
            height=480,
            jpg_bytes=b"fake_jpeg_data",
        )
        await frame_bus.publish(frame)
        await asyncio.sleep(0.01)
    
    # Wait for event collection to complete or timeout
    try:
        await asyncio.wait_for(collector_task, timeout=10.0)
    except asyncio.TimeoutError:
        pass  # It's ok if we timeout, check what we collected
    
    # Stop modules
    for module in modules:
        await module.stop()
    
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Assertions
    assert len(detections) > 0, "Should have detection results"
    assert len(tracks) > 0, "Should have track updates"
    assert len(guidances) > 0, "Should have navigation guidance"
    assert len(announcements) > 0, "Should have fusion announcements"
    
    # Verify event structure
    assert all(isinstance(d, DetectionResult) for d in detections)
    assert all(isinstance(t, TrackUpdate) for t in tracks)
    assert all(isinstance(g, NavigationGuidance) for g in guidances)
    assert all(isinstance(a, FusionAnnouncement) for a in announcements)
    
    # Verify track IDs are assigned
    track_ids = {t.track_id for t in tracks}
    assert len(track_ids) > 0, "Should have at least one unique track ID"
    
    # Verify guidance has valid urgency levels
    urgency_levels = {g.urgency for g in guidances}
    assert urgency_levels.issubset({"low", "medium", "high", "critical"})


@pytest.mark.asyncio
async def test_module_startup_shutdown():
    """Test module startup and shutdown."""
    control_state = ControlState()
    frame_bus = FrameBus()
    result_bus = ResultBus()
    
    module = ObjectDetectionModule()
    
    # Start module
    tasks = await module.start(frame_bus, result_bus, control_state)
    assert len(tasks) > 0
    assert module.running
    
    # Stop module
    await module.stop()
    assert not module.running
    
    # Cancel tasks
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


@pytest.mark.asyncio
async def test_control_state_updates():
    """Test control state updates."""
    control_state = ControlState()
    
    # Initial values
    assert control_state.paused is False
    assert control_state.speed == 1.0
    
    # Update values
    control_state.update(paused=True, speed=2.0)
    
    assert control_state.paused is True
    assert control_state.speed == 2.0
    
    # Get snapshot
    snapshot = control_state.get_snapshot()
    assert snapshot["paused"] is True
    assert snapshot["speed"] == 2.0

