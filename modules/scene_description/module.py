"""Scene description module - Generates natural language descriptions of the current scene."""

import asyncio
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from modules.base import BaseModule
from contracts.schemas import TrackUpdate, SceneDescription
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


class SceneDescriptionModule(BaseModule):
    """
    Scene description module.
    
    Subscribes to TrackUpdate events and generates periodic scene descriptions.
    Describes the overall scene: what objects are present and where they are.
    
    Example outputs:
    - "You are facing a room with a person on the left and a chair ahead on the right"
    - "Clear path ahead. Cell phone detected on the table to your right"
    - "Multiple people nearby. Laptop and cup on desk ahead"
    """
    
    name = "SceneDescription"
    
    def __init__(self, description_interval: float = 5.0):
        """
        Initialize scene description module.
        
        Args:
            description_interval: How often to generate descriptions (seconds)
        """
        self.description_interval = description_interval
        self.running = False
        self.result_bus: Optional[ResultBus] = None
        self.control_state: Optional[ControlState] = None
        
        # Track state
        self.active_tracks: Dict[int, TrackUpdate] = {}
        self.last_description_time: float = 0
    
    async def start(
        self,
        frame_bus,  # Not used, but required by interface
        result_bus: ResultBus,
        control_state: ControlState,
    ) -> List[asyncio.Task]:
        """Start the module."""
        self.result_bus = result_bus
        self.control_state = control_state
        self.running = True
        
        tasks = [
            asyncio.create_task(self._track_objects()),
            asyncio.create_task(self._generate_descriptions()),
        ]
        
        logger.info(f"{self.name} module started (interval: {self.description_interval}s)")
        return tasks
    
    async def _track_objects(self) -> None:
        """Track active objects from TrackUpdate events."""
        try:
            async for event in self.result_bus.subscribe_type(TrackUpdate):
                if not self.running:
                    break
                
                # Update or add track
                self.active_tracks[event.track_id] = event
                
                # Remove stale tracks (not updated in last 3 seconds)
                import time
                current_time = time.time() * 1000  # ms
                stale_threshold = 3000  # 3 seconds
                
                stale_ids = [
                    tid for tid, track in self.active_tracks.items()
                    if current_time - track.timestamp_ms > stale_threshold
                ]
                
                for tid in stale_ids:
                    del self.active_tracks[tid]
        
        except Exception as e:
            logger.error(f"{self.name} tracking error: {e}", exc_info=True)
    
    async def _generate_descriptions(self) -> None:
        """Periodically generate scene descriptions."""
        try:
            while self.running:
                await asyncio.sleep(self.description_interval)
                
                if self.control_state.paused:
                    continue
                
                description = self._describe_scene()
                
                if description:
                    import time
                    scene_desc = SceneDescription(
                        timestamp_ms=int(time.time() * 1000),
                        description=description,
                        object_count=len(self.active_tracks),
                        track_ids=list(self.active_tracks.keys())
                    )
                    
                    await self.result_bus.publish(scene_desc)
                    logger.debug(f"Scene: {description}")
        
        except Exception as e:
            logger.error(f"{self.name} generation error: {e}", exc_info=True)
    
    def _describe_scene(self) -> Optional[str]:
        """Generate natural language description of current scene."""
        if not self.active_tracks:
            return None
        
        # Group objects by location
        by_zone = defaultdict(list)
        by_direction = defaultdict(list)
        
        for track in self.active_tracks.values():
            direction = track.direction or "center"
            zone = track.zone or "mid"
            label = track.label
            
            by_direction[direction].append(label)
            by_zone[zone].append(label)
        
        # Build description
        parts = []
        
        # Start with overall count
        total = len(self.active_tracks)
        if total == 1:
            parts.append("One object detected")
        else:
            parts.append(f"{total} objects detected")
        
        # Describe by direction (most important)
        dir_order = ["center", "left", "right"]
        dir_descriptions = []
        
        for direction in dir_order:
            if direction in by_direction:
                objects = by_direction[direction]
                obj_summary = self._summarize_objects(objects)
                
                if direction == "center":
                    dir_descriptions.append(f"{obj_summary} ahead")
                else:
                    dir_descriptions.append(f"{obj_summary} on the {direction}")
        
        if dir_descriptions:
            parts.append(": " + ", ".join(dir_descriptions))
        
        # Add urgency note if any objects are near
        near_objects = by_zone.get("near", [])
        if near_objects:
            near_summary = self._summarize_objects(near_objects)
            parts.append(f". {near_summary} nearby")
        
        return "".join(parts)
    
    def _summarize_objects(self, objects: List[str]) -> str:
        """Summarize a list of object labels."""
        if not objects:
            return ""
        
        # Count occurrences
        counts = defaultdict(int)
        for obj in objects:
            counts[obj] += 1
        
        # Format
        items = []
        for obj, count in counts.items():
            if count == 1:
                items.append(f"a {obj}")
            else:
                items.append(f"{count} {obj}s")
        
        if len(items) == 1:
            return items[0]
        elif len(items) == 2:
            return f"{items[0]} and {items[1]}"
        else:
            return ", ".join(items[:-1]) + f", and {items[-1]}"
    
    async def stop(self) -> None:
        """Stop the module."""
        self.running = False
        logger.info(f"{self.name} module stopped")

