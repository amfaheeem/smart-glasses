"""Base module interface for all processing modules."""

import asyncio
from abc import ABC, abstractmethod
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState


class BaseModule(ABC):
    """Abstract base class for all processing modules."""
    
    name: str
    
    @abstractmethod
    async def start(
        self,
        frame_bus: FrameBus,
        result_bus: ResultBus,
        control_state: ControlState,
    ) -> list[asyncio.Task]:
        """
        Start the module and return list of tasks.
        
        Args:
            frame_bus: Bus for subscribing to frames
            result_bus: Bus for publishing/subscribing to results
            control_state: Shared control state
        
        Returns:
            List of asyncio tasks that should be awaited
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the module and clean up resources."""
        pass

