"""Object detection module with automatic YOLO/Stub detector switching."""

import asyncio
import logging
from typing import Optional
from modules.base import BaseModule

# Try to use real YOLO detector, fall back to stub if not available
try:
    from modules.object_detection.real_detectors import YOLODetector
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

from modules.object_detection.stub_detector import StubDetector
from contracts.schemas import DetectionResult
from core_platform.frame_bus import FrameBus
from core_platform.result_bus import ResultBus
from core_platform.control_state import ControlState

logger = logging.getLogger(__name__)


class ObjectDetectionModule(BaseModule):
    """
    Object detection module.
    
    Automatically uses YOLO if available, otherwise falls back to stub detector.
    """
    
    name = "ObjectDetection"
    
    def __init__(self, use_yolo: bool = True):
        self.use_yolo = use_yolo and YOLO_AVAILABLE
        
        if self.use_yolo:
            try:
                logger.info("Loading YOLO detector...")
                self.detector = YOLODetector(model_name="yolov8n.pt")
                logger.info("✓ Using YOLO detector (real ML - 80 object classes)")
            except Exception as e:
                logger.warning(f"Failed to load YOLO: {e}")
                logger.info("Falling back to stub detector")
                self.detector = StubDetector()
                self.use_yolo = False
        else:
            if not YOLO_AVAILABLE:
                logger.warning("YOLO not available (install: pip install ultralytics)")
            logger.info("Using stub detector (deterministic patterns)")
            self.detector = StubDetector()
        
        self.running = False
        self.frame_bus: Optional[FrameBus] = None
        self.result_bus: Optional[ResultBus] = None
        self.control_state: Optional[ControlState] = None
    
    async def start(
        self,
        frame_bus: FrameBus,
        result_bus: ResultBus,
        control_state: ControlState,
    ) -> list[asyncio.Task]:
        """Start the module."""
        self.frame_bus = frame_bus
        self.result_bus = result_bus
        self.control_state = control_state
        self.running = True
        
        task = asyncio.create_task(self._process_frames())
        detector_type = "YOLO (real ML)" if self.use_yolo else "Stub (demo)"
        logger.info(f"{self.name} module started using {detector_type}")
        return [task]
    
    async def _process_frames(self) -> None:
        """Process frames and publish detection results."""
        try:
            async for frame in self.frame_bus.subscribe():
                if not self.running:
                    break
                
                # Run detection
                if self.use_yolo:
                    # YOLO needs frame data
                    detections = self.detector.detect(
                        frame.frame_id,
                        frame.width,
                        frame.height,
                        frame_data=frame.jpg_bytes
                    )
                else:
                    # Stub detector doesn't need frame data
                    detections = self.detector.detect(
                        frame.frame_id,
                        frame.width,
                        frame.height
                    )
                
                # Filter by confidence threshold
                threshold = self.control_state.detection_conf_threshold
                filtered_detections = [
                    d for d in detections
                    if d.confidence >= threshold
                ]
                
                # Publish result
                result = DetectionResult(
                    frame_id=frame.frame_id,
                    timestamp_ms=frame.timestamp_ms,
                    objects=filtered_detections,
                )
                
                await self.result_bus.publish(result)
                
                if frame.frame_id % 30 == 0 and filtered_detections:
                    logger.info(
                        f"{self.name}: frame {frame.frame_id}, "
                        f"{len(filtered_detections)} detections: "
                        f"{', '.join(set(d.label for d in filtered_detections))}"
                    )
        
        except Exception as e:
            logger.error(f"{self.name} error: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Stop the module."""
        self.running = False
        logger.info(f"{self.name} module stopped")
