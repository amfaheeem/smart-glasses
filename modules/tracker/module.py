"""Tracker module."""

import asyncio
import logging
from typing import Optional
from modules.base import BaseModule
from modules.tracker.tracker import Tracker
from modules.tracker.matching import match_detections_to_tracks
from contracts.schemas import DetectionResult, TrackUpdate
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


class TrackerModule(BaseModule):
    """
    Multi-object tracking module.
    
    Subscribes to DetectionResult and publishes TrackUpdate.
    """
    
    name = "Tracker"
    
    def __init__(self):
        self.tracker = Tracker(max_age=30)
        self.running = False
        self.result_bus: Optional[ResultBus] = None
        self.control_state: Optional[ControlState] = None
    
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
        
        task = asyncio.create_task(self._process_detections())
        logger.info(f"{self.name} module started")
        return [task]
    
    async def _process_detections(self) -> None:
        """Process detection results and maintain tracks."""
        try:
            async for event in self.result_bus.subscribe_type(DetectionResult):
                if not self.running:
                    break
                
                # Prepare detections for matching
                detections = [
                    (idx, det.bbox)
                    for idx, det in enumerate(event.objects)
                ]
                
                # Get current tracks
                active_tracks = self.tracker.get_active_tracks()
                
                # Match detections to tracks
                iou_threshold = self.control_state.tracker_iou_threshold
                matches, unmatched_dets, unmatched_tracks = match_detections_to_tracks(
                    detections,
                    active_tracks,
                    iou_threshold,
                )
                
                matched_track_ids = set(matches.values())
                
                # Update matched tracks
                for det_idx, track_id in matches.items():
                    detection = event.objects[det_idx]
                    track = self.tracker.update_track(
                        track_id,
                        detection.bbox,
                        event.frame_id,
                        event.timestamp_ms,
                    )
                    
                    # Publish track update
                    await self._publish_track_update(track, event.frame_id, event.timestamp_ms)
                
                # Create new tracks for unmatched detections
                for det_idx in unmatched_dets:
                    detection = event.objects[det_idx]
                    track = self.tracker.create_track(
                        detection.label,
                        detection.bbox,
                        event.frame_id,
                        event.timestamp_ms,
                    )
                    
                    # Publish track update
                    await self._publish_track_update(track, event.frame_id, event.timestamp_ms)
                
                # Mark missed tracks
                self.tracker.mark_missed_tracks(matched_track_ids)
                
                # Evict old tracks
                evicted = self.tracker.evict_old_tracks()
                if evicted:
                    logger.debug(f"{self.name}: evicted tracks {evicted}")
                
                if event.frame_id % 100 == 0:
                    logger.debug(
                        f"{self.name}: frame {event.frame_id}, "
                        f"{len(active_tracks)} active tracks"
                    )
        
        except Exception as e:
            logger.error(f"{self.name} error: {e}", exc_info=True)
    
    async def _publish_track_update(self, track, frame_id: int, timestamp_ms: int) -> None:
        """Publish a track update."""
        velocity = track.compute_velocity()
        
        update = TrackUpdate(
            track_id=track.track_id,
            frame_id=frame_id,
            timestamp_ms=timestamp_ms,
            label=track.label,
            bbox=track.bbox,
            stable=track.stable,
            velocity=velocity,
        )
        
        await self.result_bus.publish(update)
    
    async def stop(self) -> None:
        """Stop the module."""
        self.running = False
        logger.info(f"{self.name} module stopped")

