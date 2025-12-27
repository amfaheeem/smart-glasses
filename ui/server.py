"""FastAPI server with WebSocket for UI."""

import asyncio
import base64
import json
import logging
from pathlib import Path
from typing import Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contracts.schemas import (
    FramePacket,
    DetectionResult,
    TrackUpdate,
    NavigationGuidance,
    FusionAnnouncement,
    SystemMetric,
    ControlEvent,
)
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


def create_app(
    frame_bus: FrameBus,
    result_bus: ResultBus,
    control_state: ControlState,
) -> FastAPI:
    """Create FastAPI application."""
    
    app = FastAPI(title="Smart Glasses Navigation Demo")
    
    # Mount static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Store buses in app state
    app.state.frame_bus = frame_bus
    app.state.result_bus = result_bus
    app.state.control_state = control_state
    
    # Track latest detections and tracks for overlay rendering
    app.state.latest_detections: dict[int, DetectionResult] = {}
    app.state.latest_tracks: dict[int, list[TrackUpdate]] = {}
    
    @app.get("/")
    async def index():
        """Serve main UI page."""
        return FileResponse(static_dir / "index.html")
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return JSONResponse({
            "status": "ok",
            "control_state": control_state.get_snapshot(),
        })
    
    @app.post("/control")
    async def control(event: ControlEvent):
        """Handle control events from UI."""
        try:
            if event.kind == "play":
                control_state.update(paused=False)
            elif event.kind == "pause":
                control_state.update(paused=True)
            elif event.kind == "speed" and event.value:
                speed = float(event.value.get("speed", 1.0))
                control_state.update(speed=speed)
            elif event.kind == "seek" and event.value:
                frame_id = int(event.value.get("frame_id", 0))
                control_state.update(pending_seek=frame_id)
            elif event.kind == "set_threshold" and event.value:
                control_state.update(**event.value)
            
            return JSONResponse({"status": "ok"})
        
        except Exception as e:
            logger.error(f"Control error: {e}", exc_info=True)
            return JSONResponse({"status": "error", "message": str(e)}, status_code=400)
    
    @app.get("/sources")
    async def list_sources():
        """List available video sources."""
        sources = []
        data_dir = Path("data/samples")
        
        if data_dir.exists():
            # Find MP4 files
            for mp4 in data_dir.glob("*.mp4"):
                sources.append({
                    "type": "mp4",
                    "path": str(mp4),
                    "name": mp4.name,
                })
            
            # Find frame directories
            for subdir in data_dir.iterdir():
                if subdir.is_dir() and (subdir / "metadata.json").exists():
                    sources.append({
                        "type": "frames",
                        "path": str(subdir),
                        "name": subdir.name,
                    })
        
        return JSONResponse({"sources": sources})
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for streaming data to UI."""
        await websocket.accept()
        logger.info("WebSocket client connected")
        
        try:
            # Create tasks for streaming
            frame_task = asyncio.create_task(stream_frames(websocket, frame_bus))
            event_task = asyncio.create_task(stream_events(websocket, result_bus, app.state))
            
            # Wait for either task to complete (or client disconnect)
            done, pending = await asyncio.wait(
                [frame_task, event_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
        
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
    
    return app


async def stream_frames(websocket: WebSocket, frame_bus: FrameBus) -> None:
    """Stream frames to WebSocket client at reduced rate."""
    frame_counter = 0
    frame_rate_divisor = 6  # Send every 6th frame (5 FPS if source is 30 FPS)
    
    try:
        async for frame in frame_bus.subscribe():
            frame_counter += 1
            
            # Send every Nth frame to limit bandwidth
            if frame_counter % frame_rate_divisor != 0:
                continue
            
            # Encode frame as base64
            jpg_base64 = base64.b64encode(frame.jpg_bytes).decode('utf-8')
            
            # Send to client
            await websocket.send_json({
                "type": "frame",
                "frame_id": frame.frame_id,
                "timestamp_ms": frame.timestamp_ms,
                "width": frame.width,
                "height": frame.height,
                "jpg_base64": jpg_base64,
            })
    
    except Exception as e:
        logger.error(f"Frame stream error: {e}", exc_info=True)


async def stream_events(websocket: WebSocket, result_bus: ResultBus, app_state: Any) -> None:
    """Stream events to WebSocket client."""
    try:
        async for event in result_bus.subscribe_all():
            # Store latest detections and tracks for overlay
            if isinstance(event, DetectionResult):
                app_state.latest_detections[event.frame_id] = event
                
                # Send to client
                await websocket.send_json({
                    "type": "event",
                    "event_type": "DetectionResult",
                    "data": event.model_dump(),
                })
            
            elif isinstance(event, TrackUpdate):
                if event.frame_id not in app_state.latest_tracks:
                    app_state.latest_tracks[event.frame_id] = []
                app_state.latest_tracks[event.frame_id].append(event)
                
                # Send to client
                await websocket.send_json({
                    "type": "event",
                    "event_type": "TrackUpdate",
                    "data": event.model_dump(),
                })
            
            elif isinstance(event, NavigationGuidance):
                # Send to client
                await websocket.send_json({
                    "type": "event",
                    "event_type": "NavigationGuidance",
                    "data": event.model_dump(),
                })
            
            elif isinstance(event, FusionAnnouncement):
                # Send to client
                await websocket.send_json({
                    "type": "event",
                    "event_type": "FusionAnnouncement",
                    "data": event.model_dump(),
                })
            
            elif isinstance(event, SystemMetric):
                # Send to client
                await websocket.send_json({
                    "type": "event",
                    "event_type": "SystemMetric",
                    "data": event.model_dump(),
                })
    
    except Exception as e:
        logger.error(f"Event stream error: {e}", exc_info=True)

