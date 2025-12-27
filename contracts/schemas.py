"""Message schemas for the smart glasses navigation pipeline."""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union


class FramePacket(BaseModel):
    """Frame data published by video source."""
    frame_id: int = Field(..., description="Sequential frame number")
    timestamp_ms: int = Field(..., description="Timestamp in milliseconds")
    width: int = Field(..., description="Frame width in pixels")
    height: int = Field(..., description="Frame height in pixels")
    jpg_bytes: bytes = Field(..., description="JPEG-encoded frame data")
    
    class Config:
        arbitrary_types_allowed = True


class Detection(BaseModel):
    """Single object detection."""
    label: str = Field(..., description="Object class label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bbox: tuple[float, float, float, float] = Field(
        ..., 
        description="Normalized bounding box [x, y, w, h] in range 0..1"
    )


class DetectionResult(BaseModel):
    """Detection results for a single frame."""
    frame_id: int
    timestamp_ms: int
    objects: list[Detection] = Field(default_factory=list)


class TrackUpdate(BaseModel):
    """Tracked object update."""
    track_id: int = Field(..., description="Persistent track identifier")
    frame_id: int
    timestamp_ms: int
    label: str
    bbox: tuple[float, float, float, float]
    stable: bool = Field(..., description="True if track has been seen for N+ consecutive frames")
    velocity: Optional[tuple[float, float]] = Field(
        None, 
        description="Velocity [dx, dy] per frame in normalized coordinates"
    )
    # Navigation fields (set by NavigationModule)
    direction: Optional[str] = Field(None, description="Horizontal position: left, center, right")
    zone: Optional[str] = Field(None, description="Distance zone: near, mid, far")
    movement: Optional[str] = Field(None, description="Movement: approaching, receding, stationary")
    urgency: Optional[str] = Field(None, description="Urgency: low, medium, high, critical")


class NavigationGuidance(BaseModel):
    """Spatial reasoning and navigation guidance."""
    timestamp_ms: int
    track_id: int
    label: str
    direction: Literal["left", "center", "right"] = Field(
        ..., 
        description="Horizontal position relative to camera"
    )
    zone: Literal["near", "mid", "far"] = Field(
        ..., 
        description="Distance zone based on bbox size"
    )
    movement: Literal["approaching", "receding", "stationary"] = Field(
        ..., 
        description="Movement pattern"
    )
    urgency: Literal["low", "medium", "high", "critical"] = Field(
        ..., 
        description="Urgency level for user notification"
    )
    guidance_text: str = Field(..., description="Human-readable guidance message")


class FusionAnnouncement(BaseModel):
    """Final announcement after fusion logic."""
    timestamp_ms: int
    text: str = Field(..., description="Announcement text for TTS")
    kind: Literal["object", "hazard", "navigation", "status"] = Field(
        ..., 
        description="Announcement category"
    )
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=highest)")


class ControlEvent(BaseModel):
    """Control command from UI or external source."""
    kind: Literal["play", "pause", "speed", "seek", "set_threshold", "describe_scene", "shutdown"] = Field(
        ..., 
        description="Control action type"
    )
    value: Optional[dict] = Field(None, description="Optional parameters for the control action")


class SystemMetric(BaseModel):
    """System telemetry metric."""
    timestamp_ms: int
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")


class SceneDescription(BaseModel):
    """Scene description - Natural language summary of current scene."""
    timestamp_ms: int
    description: str = Field(
        ..., 
        description="Natural language scene description"
    )
    object_count: int = Field(..., description="Number of tracked objects")
    track_ids: list[int] = Field(
        default_factory=list,
        description="Active track IDs in this description"
    )

