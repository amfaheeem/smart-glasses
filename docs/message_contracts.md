# Message Contracts

This document describes all message types used in the smart glasses navigation pipeline.

## Core Concepts

- All messages are Pydantic models (defined in `contracts/schemas.py`)
- Bounding boxes use normalized coordinates [x, y, w, h] in range 0..1
- Timestamps are in milliseconds since epoch
- All messages are immutable once created

---

## FramePacket

Video frame data published by video sources.

**Fields**:
- `frame_id: int` - Sequential frame number (starts at 0)
- `timestamp_ms: int` - Timestamp in milliseconds
- `width: int` - Frame width in pixels
- `height: int` - Frame height in pixels
- `jpg_bytes: bytes` - JPEG-encoded frame data

**Published By**: VideoSource  
**Consumed By**: ObjectDetectionModule, UI Server

**Example**:
```python
FramePacket(
    frame_id=42,
    timestamp_ms=1234567890,
    width=640,
    height=480,
    jpg_bytes=b'\xff\xd8\xff\xe0...'  # JPEG data
)
```

---

## Detection

Single object detection within a frame.

**Fields**:
- `label: str` - Object class label (e.g., "person", "door")
- `confidence: float` - Detection confidence (0.0 to 1.0)
- `bbox: tuple[float, float, float, float]` - Normalized bounding box [x, y, w, h]

**Note**: Used as a nested field in DetectionResult, not published independently.

---

## DetectionResult

All object detections for a single frame.

**Fields**:
- `frame_id: int` - Frame identifier
- `timestamp_ms: int` - Timestamp in milliseconds
- `objects: list[Detection]` - List of detected objects (can be empty)

**Published By**: ObjectDetectionModule  
**Consumed By**: TrackerModule

**Example**:
```python
DetectionResult(
    frame_id=42,
    timestamp_ms=1234567890,
    objects=[
        Detection(label="person", confidence=0.85, bbox=(0.1, 0.2, 0.15, 0.3)),
        Detection(label="door", confidence=0.92, bbox=(0.7, 0.25, 0.12, 0.4)),
    ]
)
```

---

## TrackUpdate

Tracked object with persistent ID across frames.

**Fields**:
- `track_id: int` - Persistent track identifier (starts at 1)
- `frame_id: int` - Current frame identifier
- `timestamp_ms: int` - Timestamp in milliseconds
- `label: str` - Object class label
- `bbox: tuple[float, float, float, float]` - Normalized bounding box [x, y, w, h]
- `stable: bool` - True if track seen for 3+ consecutive frames
- `velocity: tuple[float, float] | None` - Velocity [dx, dy] per frame (None if insufficient history)

**Published By**: TrackerModule  
**Consumed By**: NavigationModule, FusionModule

**Example**:
```python
TrackUpdate(
    track_id=5,
    frame_id=42,
    timestamp_ms=1234567890,
    label="person",
    bbox=(0.12, 0.22, 0.15, 0.3),
    stable=True,
    velocity=(0.01, 0.002)  # Moving right and slightly down
)
```

---

## NavigationGuidance

Spatial reasoning and navigation guidance for a tracked object.

**Fields**:
- `timestamp_ms: int` - Timestamp in milliseconds
- `track_id: int` - Associated track identifier
- `label: str` - Object class label
- `direction: "left" | "center" | "right"` - Horizontal position relative to camera
- `zone: "near" | "mid" | "far"` - Distance zone based on bbox size
- `movement: "approaching" | "receding" | "stationary"` - Movement pattern
- `urgency: "low" | "medium" | "high" | "critical"` - Priority level
- `guidance_text: str` - Human-readable guidance message

**Published By**: NavigationModule  
**Consumed By**: FusionModule

**Example**:
```python
NavigationGuidance(
    timestamp_ms=1234567890,
    track_id=5,
    label="person",
    direction="left",
    zone="mid",
    movement="approaching",
    urgency="medium",
    guidance_text="person approaching on left"
)
```

**Urgency Rules**:
- `critical`: near zone + approaching movement
- `high`: near zone (any movement)
- `medium`: mid zone + approaching movement
- `low`: all other combinations

---

## FusionAnnouncement

Final announcement after fusion policy (cooldown, prioritization).

**Fields**:
- `timestamp_ms: int` - Timestamp in milliseconds
- `text: str` - Announcement text for TTS or display
- `kind: "object" | "hazard" | "navigation" | "status"` - Announcement category
- `priority: int` - Priority level (1=highest, 5=lowest)

**Published By**: FusionModule  
**Consumed By**: UI Server, (future: TTS, haptics)

**Example**:
```python
FusionAnnouncement(
    timestamp_ms=1234567890,
    text="person approaching on left",
    kind="object",
    priority=2
)
```

**Kind Classification**:
- `hazard`: Labels like "hazard", "obstacle"
- `object`: Labels like "person", "vehicle"
- `navigation`: Other navigational elements (doors, landmarks)
- `status`: System status messages

---

## ControlEvent

Control command from UI or external controller.

**Fields**:
- `kind: "play" | "pause" | "speed" | "seek" | "set_threshold"` - Control action type
- `value: dict | None` - Optional parameters for the action

**Published By**: UI (HTTP endpoint)  
**Consumed By**: ControlState (shared mutable state)

**Examples**:
```python
# Play
ControlEvent(kind="play", value=None)

# Pause
ControlEvent(kind="pause", value=None)

# Change speed
ControlEvent(kind="speed", value={"speed": 2.0})

# Seek to frame
ControlEvent(kind="seek", value={"frame_id": 100})

# Update thresholds
ControlEvent(kind="set_threshold", value={
    "detection_conf_threshold": 0.7,
    "tracker_iou_threshold": 0.4,
    "fusion_cooldown_seconds": 5.0
})
```

---

## SystemMetric

Telemetry metric for monitoring system performance.

**Fields**:
- `timestamp_ms: int` - Timestamp in milliseconds
- `name: str` - Metric name (e.g., "fusion.announcements.count")
- `value: float` - Metric value

**Published By**: Any module  
**Consumed By**: UI Server, (future: monitoring/logging)

**Example**:
```python
SystemMetric(
    timestamp_ms=1234567890,
    name="fusion.announcements.count",
    value=42.0
)
```

---

## Coordinate Systems

### Normalized Bounding Boxes

All bounding boxes use normalized coordinates to be resolution-independent:

```
bbox = (x, y, w, h)

where:
  x = left edge / frame_width       (0.0 to 1.0)
  y = top edge / frame_height       (0.0 to 1.0)
  w = box_width / frame_width       (0.0 to 1.0)
  h = box_height / frame_height     (0.0 to 1.0)
```

**Example**: For a 640x480 frame with a box at pixel coordinates (100, 150, 80, 120):
```python
normalized_bbox = (100/640, 150/480, 80/640, 120/480)
                = (0.156, 0.3125, 0.125, 0.25)
```

### Velocity

Velocity is expressed in normalized coordinates per frame:
```python
velocity = (dx, dy)

where:
  dx = change in center_x per frame
  dy = change in center_y per frame
```

Positive dx = moving right  
Negative dx = moving left  
Positive dy = moving down  
Negative dy = moving up

---

## Type-Safe Usage

All contracts are Pydantic models with validation:

```python
# Valid
detection = Detection(
    label="person",
    confidence=0.85,
    bbox=(0.1, 0.2, 0.15, 0.3)
)

# Raises ValidationError - confidence out of range
detection = Detection(
    label="person",
    confidence=1.5,  # Must be 0.0 to 1.0
    bbox=(0.1, 0.2, 0.15, 0.3)
)

# Raises ValidationError - invalid urgency
guidance = NavigationGuidance(
    timestamp_ms=123,
    track_id=1,
    label="person",
    direction="left",
    zone="mid",
    movement="approaching",
    urgency="super-urgent",  # Must be literal: low/medium/high/critical
    guidance_text="test"
)
```

