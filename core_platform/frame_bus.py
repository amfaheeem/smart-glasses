"""Frame bus - Latest-frame-wins pub-sub for video frames."""

import asyncio
import logging
from typing import AsyncIterator, Optional
from contracts.schemas import FramePacket

logger = logging.getLogger(__name__)


class FrameBus:
    """
    Pub-sub bus for video frames with latest-frame-wins behavior.
    
    Subscribers get the latest frame, old frames are dropped if not consumed.
    This prevents backpressure from slow consumers.
    """
    
    def __init__(self, queue_size: int = 2):
        self.queue_size = queue_size
        self.subscribers: Optional[list[asyncio.Queue[FramePacket]]] = []
        self._lock = asyncio.Lock()
        self._frame_count = 0
        self._dropped_count = 0
    
    async def publish(self, frame: FramePacket) -> None:
        """Publish a frame to all subscribers."""
        async with self._lock:
            self._frame_count += 1
            
            for queue in self.subscribers:
                # Drop oldest frame if queue is full
                if queue.qsize() >= self.queue_size:
                    try:
                        queue.get_nowait()
                        self._dropped_count += 1
                    except asyncio.QueueEmpty:
                        pass
                
                try:
                    queue.put_nowait(frame)
                except asyncio.QueueFull:
                    # Should not happen after we just made space
                    logger.warning(f"Frame queue full for subscriber, dropping frame {frame.frame_id}")
                    self._dropped_count += 1
    
    async def subscribe(self) -> AsyncIterator[FramePacket]:
        """
        Subscribe to frame updates.
        
        Yields frames as they are published. Old frames may be dropped.
        """
        queue: Optional[asyncio.Queue[FramePacket]] = asyncio.Queue(maxsize=self.queue_size)
        
        async with self._lock:
            self.subscribers.append(queue)
        
        try:
            while True:
                frame = await queue.get()
                if frame is None:  # Shutdown signal
                    break
                yield frame
        finally:
            async with self._lock:
                if queue in self.subscribers:
                    self.subscribers.remove(queue)
    
    async def shutdown(self) -> None:
        """Signal all subscribers to stop."""
        async with self._lock:
            for queue in self.subscribers:
                try:
                    queue.put_nowait(None)
                except asyncio.QueueFull:
                    pass
            
            logger.info(
                f"FrameBus stats - Published: {self._frame_count}, "
                f"Dropped: {self._dropped_count}"
            )

