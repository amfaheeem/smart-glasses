"""YOLO detector - Real ML-based object detection using Ultralytics YOLO."""

import logging
from typing import List
import numpy as np
from contracts.schemas import Detection

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics YOLO not installed. Install with: pip install ultralytics")


class YOLODetector:
    """
    Real object detector using YOLO (You Only Look Once).
    
    Supports YOLOv8 models: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    - n = nano (fastest, least accurate)
    - s = small
    - m = medium
    - l = large
    - x = extra large (slowest, most accurate)
    """
    
    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.5):
        """
        Initialize YOLO detector.
        
        Args:
            model_name: YOLO model to use (e.g., "yolov8n.pt", "yolov8s.pt")
            conf_threshold: Minimum confidence threshold (will be overridden by ControlState)
        """
        if not YOLO_AVAILABLE:
            raise ImportError(
                "Ultralytics YOLO not installed. "
                "Install with: pip install ultralytics"
            )
        
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        
        logger.info(f"Loading YOLO model: {model_name}")
        self.model = YOLO(model_name)
        logger.info(f"✓ YOLO model loaded successfully")
    
    def detect(self, frame_id: int, width: int, height: int, frame_data: bytes = None) -> List[Detection]:
        """
        Detect objects in frame.
        
        Note: For YOLO, we need the actual image data, not just frame_id.
        The module will need to pass the decoded frame.
        
        Args:
            frame_id: Frame identifier (for logging)
            width: Frame width
            height: Frame height
            frame_data: JPEG bytes (will be decoded)
        
        Returns:
            List of Detection objects
        """
        if frame_data is None:
            logger.warning("No frame data provided to YOLO detector")
            return []
        
        # Decode JPEG bytes to numpy array
        import cv2
        nparr = np.frombuffer(frame_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.warning(f"Failed to decode frame {frame_id}")
            return []
        
        # Run YOLO detection
        results = self.model(img, verbose=False)[0]
        
        detections = []
        
        # Convert YOLO results to Detection objects
        for box in results.boxes:
            # Get bounding box coordinates (xyxy format)
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            # Convert to normalized xywh format
            x = float(x1 / width)
            y = float(y1 / height)
            w = float((x2 - x1) / width)
            h = float((y2 - y1) / height)
            
            # Get confidence and class
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = self.model.names[class_id]
            
            detection = Detection(
                label=label,
                confidence=confidence,
                bbox=(x, y, w, h)
            )
            detections.append(detection)
        
        return detections


class TFLiteDetector:
    """
    TensorFlow Lite detector for Raspberry Pi / edge devices.
    
    Uses pre-trained TFLite models (SSD MobileNet, etc.)
    Optimized for low-power devices.
    """
    
    def __init__(self, model_path: str, labels_path: str):
        """
        Initialize TFLite detector.
        
        Args:
            model_path: Path to .tflite model file
            labels_path: Path to labels.txt file
        """
        try:
            import tflite_runtime.interpreter as tflite
            self.tflite = tflite
        except ImportError:
            try:
                import tensorflow.lite as tflite
                self.tflite = tflite
            except ImportError:
                raise ImportError(
                    "TFLite not installed. "
                    "Install with: pip install tflite-runtime"
                )
        
        # Load model
        self.interpreter = self.tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        # Get input/output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load labels
        with open(labels_path, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        
        logger.info(f"✓ TFLite model loaded: {model_path}")
    
    def detect(self, frame_id: int, width: int, height: int, frame_data: bytes = None) -> List[Detection]:
        """Detect objects using TFLite model."""
        import cv2
        
        # Decode frame
        nparr = np.frombuffer(frame_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []
        
        # Preprocess for model input
        input_shape = self.input_details[0]['shape']
        input_img = cv2.resize(img, (input_shape[1], input_shape[2]))
        input_img = np.expand_dims(input_img, axis=0)
        
        if self.input_details[0]['dtype'] == np.uint8:
            input_img = input_img.astype(np.uint8)
        else:
            input_img = (input_img.astype(np.float32) - 127.5) / 127.5
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_img)
        self.interpreter.invoke()
        
        # Get outputs
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
        
        detections = []
        for i in range(len(scores)):
            if scores[i] > 0.5:  # Confidence threshold
                y1, x1, y2, x2 = boxes[i]
                
                detection = Detection(
                    label=self.labels[int(classes[i])],
                    confidence=float(scores[i]),
                    bbox=(float(x1), float(y1), float(x2 - x1), float(y2 - y1))
                )
                detections.append(detection)
        
        return detections


class OpenCVDNNDetector:
    """
    OpenCV DNN detector - Works with pre-trained models.
    
    Supports:
    - YOLO (Darknet)
    - SSD (TensorFlow)
    - Caffe models
    
    Good balance between performance and ease of use.
    """
    
    def __init__(self, model_path: str, config_path: str, labels_path: str, framework: str = "darknet"):
        """
        Initialize OpenCV DNN detector.
        
        Args:
            model_path: Path to model weights
            config_path: Path to model config
            labels_path: Path to class labels
            framework: "darknet", "tensorflow", or "caffe"
        """
        import cv2
        
        # Load model
        if framework == "darknet":
            self.net = cv2.dnn.readNetFromDarknet(config_path, model_path)
        elif framework == "tensorflow":
            self.net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
        elif framework == "caffe":
            self.net = cv2.dnn.readNetFromCaffe(config_path, model_path)
        else:
            raise ValueError(f"Unknown framework: {framework}")
        
        # Set backend (use CUDA if available)
        try:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            logger.info("Using CUDA backend")
        except:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            logger.info("Using CPU backend")
        
        # Load labels
        with open(labels_path, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        
        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        logger.info(f"✓ OpenCV DNN model loaded")
    
    def detect(self, frame_id: int, width: int, height: int, frame_data: bytes = None) -> List[Detection]:
        """Detect objects using OpenCV DNN."""
        import cv2
        
        # Decode frame
        nparr = np.frombuffer(frame_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []
        
        # Create blob
        blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        
        # Forward pass
        outputs = self.net.forward(self.output_layers)
        
        detections = []
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:
                    # Get bbox
                    center_x = detection[0]
                    center_y = detection[1]
                    w = detection[2]
                    h = detection[3]
                    
                    # Convert to top-left corner format
                    x = center_x - w / 2
                    y = center_y - h / 2
                    
                    det = Detection(
                        label=self.labels[class_id],
                        confidence=float(confidence),
                        bbox=(float(x), float(y), float(w), float(h))
                    )
                    detections.append(det)
        
        return detections

