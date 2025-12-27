"""Tests for frame and result buses."""

import pytest
import asyncio
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from contracts.schemas import FramePacket, DetectionResult, Detection


@pytest.mark.asyncio
async def test_frame_bus_publish_subscribe():
    """Test frame bus basic pub-sub."""
    bus = FrameBus(queue_size=2)
    
    # Create a subscriber
    frames_received = []
    
    async def subscriber():
        async for frame in bus.subscribe():
            frames_received.append(frame)
            if len(frames_received) >= 3:
                break
    
    # Start subscriber
    sub_task = asyncio.create_task(subscriber())
    
    # Give subscriber time to start
    await asyncio.sleep(0.01)
    
    # Publish frames
    for i in range(3):
        frame = FramePacket(
            frame_id=i,
            timestamp_ms=i * 33,
            width=640,
            height=480,
            jpg_bytes=b"fake",
        )
        await bus.publish(frame)
        await asyncio.sleep(0.01)
    
    # Wait for subscriber
    await sub_task
    
    assert len(frames_received) == 3
    assert frames_received[0].frame_id == 0
    assert frames_received[2].frame_id == 2


@pytest.mark.asyncio
async def test_frame_bus_drop_old_frames():
    """Test that old frames are dropped when queue is full."""
    bus = FrameBus(queue_size=2)
    
    frames_received = []
    
    async def slow_subscriber():
        async for frame in bus.subscribe():
            frames_received.append(frame)
            await asyncio.sleep(0.1)  # Slow consumer
            if len(frames_received) >= 3:
                break
    
    # Start subscriber
    sub_task = asyncio.create_task(slow_subscriber())
    await asyncio.sleep(0.01)
    
    # Publish many frames quickly
    for i in range(10):
        frame = FramePacket(
            frame_id=i,
            timestamp_ms=i * 33,
            width=640,
            height=480,
            jpg_bytes=b"fake",
        )
        await bus.publish(frame)
        await asyncio.sleep(0.01)
    
    # Wait for subscriber
    await sub_task
    
    # Should have received frames, but not all (some dropped)
    assert len(frames_received) == 3
    # Frames should not be consecutive due to dropping
    assert bus._dropped_count > 0


@pytest.mark.asyncio
async def test_result_bus_publish_subscribe():
    """Test result bus basic pub-sub."""
    bus = ResultBus(queue_size=100)
    
    events_received = []
    
    async def subscriber():
        async for event in bus.subscribe_all():
            events_received.append(event)
            if len(events_received) >= 3:
                break
    
    # Start subscriber
    sub_task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.01)
    
    # Publish events
    for i in range(3):
        result = DetectionResult(
            frame_id=i,
            timestamp_ms=i * 33,
            objects=[],
        )
        await bus.publish(result)
        await asyncio.sleep(0.01)
    
    # Wait for subscriber
    await sub_task
    
    assert len(events_received) == 3
    assert all(isinstance(e, DetectionResult) for e in events_received)


@pytest.mark.asyncio
async def test_result_bus_type_filter():
    """Test result bus type-filtered subscription."""
    bus = ResultBus(queue_size=100)
    
    detections_received = []
    
    async def subscriber():
        async for detection in bus.subscribe_type(DetectionResult):
            detections_received.append(detection)
            if len(detections_received) >= 2:
                break
    
    # Start subscriber
    sub_task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.01)
    
    # Publish mixed events
    await bus.publish(DetectionResult(frame_id=0, timestamp_ms=0, objects=[]))
    await bus.publish(DetectionResult(frame_id=1, timestamp_ms=33, objects=[]))
    
    # Wait for subscriber
    await sub_task
    
    assert len(detections_received) == 2
    assert all(isinstance(e, DetectionResult) for e in detections_received)

