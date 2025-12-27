"""Fusion module."""

import asyncio
import logging
from typing import Optional
from modules.base import BaseModule
from modules.fusion.policy import FusionPolicy
from contracts.schemas import NavigationGuidance, FusionAnnouncement, SystemMetric, TrackUpdate
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


class FusionModule(BaseModule):
    """
    Fusion module - Combines information and generates announcements.
    
    Subscribes to NavigationGuidance and publishes FusionAnnouncement.
    """
    
    name = "Fusion"
    
    def __init__(self):
        self.policy = FusionPolicy()
        self.running = False
        self.result_bus: Optional[ResultBus] = None
        self.control_state: Optional[ControlState] = None
        
        # Track stability info
        self.track_stability: dict[int, bool] = {}
    
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
        
        # Start two tasks: one for navigation guidance, one for track updates
        task1 = asyncio.create_task(self._process_guidance())
        task2 = asyncio.create_task(self._monitor_track_stability())
        
        logger.info(f"{self.name} module started")
        return [task1, task2]
    
    async def _monitor_track_stability(self) -> None:
        """Monitor track updates to maintain stability info."""
        try:
            async for event in self.result_bus.subscribe_type(TrackUpdate):
                if not self.running:
                    break
                
                self.track_stability[event.track_id] = event.stable
        
        except Exception as e:
            logger.error(f"{self.name} stability monitor error: {e}", exc_info=True)
    
    async def _process_guidance(self) -> None:
        """Process navigation guidance and generate announcements."""
        try:
            async for guidance in self.result_bus.subscribe_type(NavigationGuidance):
                if not self.running:
                    break
                
                # Get track stability
                stable = self.track_stability.get(guidance.track_id, False)
                
                # Check if should announce
                cooldown_ms = int(self.control_state.fusion_cooldown_seconds * 1000)
                
                should_announce = self.policy.should_announce(
                    guidance.track_id,
                    guidance.timestamp_ms,
                    guidance.urgency,
                    stable,
                    cooldown_ms,
                )
                
                if should_announce:
                    # Get priority and kind
                    priority = self.policy.get_priority(guidance.urgency)
                    kind = self.policy.get_announcement_kind(guidance.label)
                    
                    # Create announcement
                    announcement = FusionAnnouncement(
                        timestamp_ms=guidance.timestamp_ms,
                        text=guidance.guidance_text,
                        kind=kind,
                        priority=priority,
                    )
                    
                    await self.result_bus.publish(announcement)
                    
                    # Record announcement
                    self.policy.record_announcement(
                        guidance.track_id,
                        guidance.timestamp_ms,
                    )
                    
                    logger.debug(
                        f"{self.name}: announced - {guidance.guidance_text} "
                        f"(priority {priority})"
                    )
                
                # Publish metric every 100 announcements
                if self.policy.announcement_count % 100 == 0 and self.policy.announcement_count > 0:
                    metric = SystemMetric(
                        timestamp_ms=guidance.timestamp_ms,
                        name="fusion.announcements.count",
                        value=float(self.policy.announcement_count),
                    )
                    await self.result_bus.publish(metric)
        
        except Exception as e:
            logger.error(f"{self.name} error: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Stop the module."""
        self.running = False
        logger.info(
            f"{self.name} module stopped - "
            f"total announcements: {self.policy.announcement_count}"
        )

