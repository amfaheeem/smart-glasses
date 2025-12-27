"""YOLOv8-World detector with custom classes (open vocabulary detection)."""

import logging
from typing import List
import numpy as np
from contracts.schemas import Detection

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLOWorld
    YOLO_WORLD_AVAILABLE = True
except ImportError:
    YOLO_WORLD_AVAILABLE = False
    logger.warning("YOLOWorld not available (requires ultralytics>=8.0.238)")


class YOLOWorldDetector:
    """
    YOLO-World detector - Detects ANY object using text prompts.
    
    Unlike regular YOLO (limited to 80 COCO classes), YOLO-World can detect
    custom objects like "keys", "charger", "wallet", "glasses", etc.
    
    Uses CLIP embeddings for open-vocabulary detection.
    """
    
    def __init__(
        self,
        model_name: str = "yolov8s-world.pt",
        custom_classes: List[str] = None
    ):
        """
        Initialize YOLO-World detector.
        
        Args:
            model_name: Model to use (yolov8s-world.pt, yolov8m-world.pt, yolov8l-world.pt)
            custom_classes: List of custom object names to detect
                           e.g., ["keys", "charger", "cable", "wallet", "glasses"]
        """
        if not YOLO_WORLD_AVAILABLE:
            raise ImportError(
                "YOLOWorld not available. "
                "Upgrade ultralytics: pip install -U ultralytics"
            )
        
        self.model_name = model_name
        
        # Default classes if none provided
        if custom_classes is None:
            custom_classes = [
                # Original COCO classes (most common)
                "person", "chair", "cup", "laptop", "cell phone", 
                "keyboard", "mouse", "book", "bottle",
                # Custom classes not in COCO
                "keys", "charger", "cable", "wallet", "glasses",
                "pen", "pencil", "paper", "card", "headphones"
            ]
        
        self.custom_classes = custom_classes
        
        logger.info(f"Loading YOLO-World model: {model_name}")
        self.model = YOLOWorld(model_name)
        
        # Set custom classes
        self.model.set_classes(custom_classes)
        
        logger.info(f"✓ YOLO-World loaded with {len(custom_classes)} custom classes")
        logger.info(f"  Detecting: {', '.join(custom_classes[:10])}...")
    
    def detect(
        self,
        frame_id: int,
        width: int,
        height: int,
        frame_data: bytes = None
    ) -> List[Detection]:
        """
        Detect custom objects in frame.
        
        Args:
            frame_id: Frame identifier
            width: Frame width
            height: Frame height
            frame_data: JPEG bytes
        
        Returns:
            List of Detection objects
        """
        if frame_data is None:
            logger.warning("No frame data provided")
            return []
        
        # Decode JPEG bytes
        import cv2
        nparr = np.frombuffer(frame_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.warning(f"Failed to decode frame {frame_id}")
            return []
        
        # Run YOLO-World detection
        results = self.model(img, verbose=False)[0]
        
        detections = []
        
        for box in results.boxes:
            # Get bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            # Convert to normalized xywh
            x = float(x1 / width)
            y = float(y1 / height)
            w = float((x2 - x1) / width)
            h = float((y2 - y1) / height)
            
            # Get confidence and class
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            
            # Get label from custom classes
            if class_id < len(self.custom_classes):
                label = self.custom_classes[class_id]
            else:
                label = f"object_{class_id}"
            
            detection = Detection(
                label=label,
                confidence=confidence,
                bbox=(x, y, w, h)
            )
            detections.append(detection)
        
        return detections
    
    def update_classes(self, new_classes: List[str]) -> None:
        """
        Update the classes to detect at runtime.
        
        Useful for switching detection modes dynamically.
        
        Example:
            # Indoor mode
            detector.update_classes(["keys", "phone", "laptop", "cup"])
            
            # Outdoor mode  
            detector.update_classes(["car", "bicycle", "person", "dog"])
        """
        self.custom_classes = new_classes
        self.model.set_classes(new_classes)
        logger.info(f"Updated classes: {', '.join(new_classes)}")


# Preset class configurations for different scenarios

INDOOR_CLASSES = [
    "person", "chair", "couch", "table", "laptop", "cell phone",
    "keyboard", "mouse", "cup", "bottle", "book", "clock",
    "keys", "charger", "cable", "wallet", "glasses", "headphones"
]

OUTDOOR_CLASSES = [
    "person", "car", "bicycle", "motorcycle", "bus", "truck",
    "traffic light", "stop sign", "bench", "backpack", "umbrella",
    "handbag", "dog", "cat"
]

KITCHEN_CLASSES = [
    "cup", "bottle", "bowl", "knife", "fork", "spoon",
    "microwave", "oven", "refrigerator", "sink", "kettle",
    "toaster", "cutting board", "dish", "pan", "pot"
]

OFFICE_CLASSES = [
    "laptop", "keyboard", "mouse", "monitor", "printer",
    "cell phone", "tablet", "pen", "pencil", "paper",
    "notebook", "stapler", "scissors", "folder", "charger"
]

ACCESSIBILITY_CLASSES = [
    # For blind navigation - obstacles and important objects
    "person", "door", "stairs", "chair", "table", "wall",
    "pole", "sign", "curb", "vehicle", "bicycle", "obstacle"
]

