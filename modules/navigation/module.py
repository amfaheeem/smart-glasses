"""Navigation module."""

import asyncio
import logging
from typing import Optional
from modules.base import BaseModule
from modules.navigation.spatial import (
    analyze_direction,
    analyze_zone,
    analyze_movement,
    compute_urgency,
)
from modules.navigation.guidance import generate_guidance_text
from contracts.schemas import TrackUpdate, NavigationGuidance
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


class NavigationModule(BaseModule):
    """
    Navigation and spatial reasoning module.
    
    Subscribes to TrackUpdate and publishes NavigationGuidance.
    """
    
    name = "Navigation"
    
    def __init__(self):
        self.running = False
        self.result_bus: Optional[ResultBus] = None
        self.control_state: Optional[ControlState] = None
        
        # Store track history for movement analysis
        self.track_history: dict[int, list[dict]] = {}
    
    async def start(
        self,
        frame_bus: FrameBus,
        result_bus: ResultBus,
        control_state: ControlState,
    ) -> list[asyncio.Task]:
        """Start the module."""
        self.result_bus = result_bus
        self.control_state = control_state
        self.running = True
        
        task = asyncio.create_task(self._process_tracks())
        logger.info(f"{self.name} module started")
        return [task]
    
    async def _process_tracks(self) -> None:
        """Process track updates and generate navigation guidance."""
        try:
            async for event in self.result_bus.subscribe_type(TrackUpdate):
                if not self.running:
                    break
                
                # Update track history
                if event.track_id not in self.track_history:
                    self.track_history[event.track_id] = []
                
                self.track_history[event.track_id].append({
                    "bbox": event.bbox,
                    "frame_id": event.frame_id,
                    "timestamp_ms": event.timestamp_ms,
                })
                
                # Keep only recent history (last 5 entries)
                if len(self.track_history[event.track_id]) > 5:
                    self.track_history[event.track_id] = self.track_history[event.track_id][-5:]
                
                # Analyze spatial properties
                direction = analyze_direction(event.bbox)
                zone = analyze_zone(event.bbox)
                movement = analyze_movement(
                    event.bbox,
                    self.track_history[event.track_id]
                )
                urgency = compute_urgency(zone, movement)
                
                # Generate guidance text
                guidance_text = generate_guidance_text(
                    event.label,
                    direction,
                    zone,
                    movement,
                )
                
                # Create guidance event
                guidance = NavigationGuidance(
                    timestamp_ms=event.timestamp_ms,
                    track_id=event.track_id,
                    label=event.label,
                    direction=direction,
                    zone=zone,
                    movement=movement,
                    urgency=urgency,
                    guidance_text=guidance_text,
                )
                
                await self.result_bus.publish(guidance)
                
                if event.frame_id % 100 == 0:
                    logger.debug(
                        f"{self.name}: frame {event.frame_id}, "
                        f"track {event.track_id} - {guidance_text}"
                    )
        
        except Exception as e:
            logger.error(f"{self.name} error: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Stop the module."""
        self.running = False
        logger.info(f"{self.name} module stopped")

