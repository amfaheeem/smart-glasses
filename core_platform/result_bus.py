"""Result bus - Typed event pub-sub for processing results."""

import asyncio
import logging
from typing import AsyncIterator, Type, TypeVar, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ResultBus:
    """
    Pub-sub bus for typed events (detection results, tracks, guidance, etc.).
    
    Supports type-filtered subscriptions.
    """
    
    def __init__(self, queue_size: int = 100):
        self.queue_size = queue_size
        self.subscribers: Optional[list[asyncio.Queue[BaseModel]]] = []
        self._lock = asyncio.Lock()
        self._event_count = 0
    
    async def publish(self, event: BaseModel) -> None:
        """Publish an event to all subscribers."""
        async with self._lock:
            self._event_count += 1
            
            for queue in self.subscribers:
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    logger.warning(
                        f"Result queue full for subscriber, dropping event "
                        f"{type(event).__name__}"
                    )
    
    async def subscribe_all(self) -> AsyncIterator[BaseModel]:
        """Subscribe to all events."""
        queue: Optional[asyncio.Queue[BaseModel]] = asyncio.Queue(maxsize=self.queue_size)
        
        async with self._lock:
            self.subscribers.append(queue)
        
        try:
            while True:
                event = await queue.get()
                if event is None:  # Shutdown signal
                    break
                yield event
        finally:
            async with self._lock:
                if queue in self.subscribers:
                    self.subscribers.remove(queue)
    
    async def subscribe_type(self, event_type: Type[T]) -> AsyncIterator[T]:
        """Subscribe to events of a specific type."""
        async for event in self.subscribe_all():
            if isinstance(event, event_type):
                yield event
    
    async def shutdown(self) -> None:
        """Signal all subscribers to stop."""
        async with self._lock:
            for queue in self.subscribers:
                try:
                    queue.put_nowait(None)
                except asyncio.QueueFull:
                    pass
            
            logger.info(f"ResultBus stats - Published: {self._event_count} events")

