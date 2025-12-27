# System Architecture - Component Status

This document provides a quick reference for which components are implemented vs future.

---

## ✅ IMPLEMENTED COMPONENTS (Working Now)

### Core Infrastructure
- **FrameBus** - Video frame distribution (latest-frame-wins)
- **ResultBus** - Event pub-sub system (typed subscriptions)
- **ControlState** - Shared configuration and settings
- **Clock** - Timestamp utilities

### Input Sources
- **Camera Source** - Live webcam capture
- **Video Source** - MP4 file replay
- **Frame Directory Source** - JPEG sequence replay

### Perception Pipeline
- **Object Detection Module** - YOLO (80 classes) or custom classes
- **Tracker Module** - Multi-object tracking with IoU matching
- **Spatial Analysis Module** - Object position analysis (direction, zone, urgency)
  - **NOTE**: Renamed from "Navigation" to avoid confusion with map-based navigation
  - Analyzes object positions **relative to camera**
  - Does NOT do path planning or routing

### Fusion & Output
- **Fusion Module** - Cooldown logic, priority-based announcements
- **Scene Description Module** - Natural language scene summaries
- **Voice Output Module** - Text-to-speech (pyttsx3)
- **Voice Input Module** - Speech recognition (Google API)

---

## 📋 FUTURE COMPONENTS (Designed But Not Implemented)

### Additional Input Sources
- **IMU/Sensors** - Accelerometer, gyroscope for motion tracking
- **RFID Reader** - Tag detection for object identification
- **WiFi/BLE Beacons** - Indoor positioning

### Sensor Fusion
- **RFID Detection Module** - Tag scanning and object identification
- **Sensor Fusion Module** - Combine visual + RFID detections

### Localization Pipeline (Map-Based Navigation)
- **SLAM Module** - Visual odometry, camera pose estimation
- **Localization Module** - Fuse SLAM + IMU + WiFi for position on map
- **Map Manager** - Load and query indoor floor plans

### Navigation Pipeline (Map-Based Navigation)
- **Path Planner Module** - A* algorithm for route planning
- **Obstacle Avoidance Module** - Dynamic replanning around obstacles
- **Navigation Guidance Module** - Turn-by-turn instructions

### Interface
- **Web UI Frontend** - Browser-based visual display
  - Backend partially exists, frontend not implemented
  - Will show live video, bounding boxes, event feed

---

## 🔄 INTEGRATION POINTS (Already Prepared)

The architecture is designed for seamless integration of future components:

### 1. Voice Input → Navigation
```python
# Voice Input already publishes ControlEvent
# Just add handling for navigation requests:
ControlEvent(
    kind="navigate_to",
    value={"destination": "Conference Room 301"}
)

# Future Navigation module subscribes automatically via ResultBus
```

### 2. Spatial Analysis → Obstacle Avoidance
```python
# Spatial Analysis publishes SpatialGuidance
SpatialGuidance(
    label="person",
    direction="center",
    urgency="critical"  # Blocking path!
)

# Future Obstacle Avoidance subscribes and replans route
```

### 3. Navigation → Voice Output
```python
# Future Navigation publishes NavigationInstruction
NavigationInstruction(
    instruction_text="Turn right in 5 meters",
    distance_to_action_m=5.0
)

# Voice Output will automatically speak it (add subscription)
```

### 4. SLAM → FrameBus
```python
# SLAM will subscribe to FrameBus (same as Object Detection)
async for frame in frame_bus.subscribe():
    # Track visual features for position estimation
    pass
```

---

## 📊 Module Responsibility Matrix

| Module | Input | Processing | Output | Status |
|--------|-------|------------|--------|--------|
| **Object Detection** | Video frames | YOLO neural network | DetectionResult | ✅ Implemented |
| **Tracker** | DetectionResult | IoU matching | TrackUpdate | ✅ Implemented |
| **Spatial Analysis** | TrackUpdate | Geometric analysis | SpatialGuidance | ✅ Implemented |
| **Fusion** | SpatialGuidance | Cooldown + priority | FusionAnnouncement | ✅ Implemented |
| **Scene Description** | TrackUpdate | Rule-based summary | SceneDescription | ✅ Implemented |
| **Voice Input** | Microphone | Speech recognition | ControlEvent | ✅ Implemented |
| **Voice Output** | Announcements | Text-to-speech | Audio | ✅ Implemented |
| **SLAM** | Video frames | Feature tracking | LocalizationUpdate | 📋 Future |
| **Localization** | LocalizationUpdate + IMU | Sensor fusion | UserLocation | 📋 Future |
| **Map Manager** | Map files | Spatial queries | Map data | 📋 Future |
| **Path Planner** | UserLocation + destination | A* algorithm | PlannedRoute | 📋 Future |
| **Obstacle Avoidance** | SpatialGuidance + route | Collision detection | UpdatedRoute | 📋 Future |
| **Navigation Guidance** | UserLocation + route | Instruction generation | NavigationInstruction | 📋 Future |

---

## 🎯 Key Architectural Decisions

### 1. Renamed "Navigation" to "Spatial Analysis"
**Why**: Avoid confusion between:
- **Spatial Analysis** (current): Object-relative positioning ("chair on right")
- **Navigation** (future): Map-based routing ("turn right in 5 meters")

### 2. ResultBus as Integration Layer
**Why**: Future modules can be added without modifying existing code
- Just publish new message types
- Existing modules subscribe if interested
- Clean separation of concerns

### 3. SLAM Subscribes to FrameBus
**Why**: SLAM needs raw video frames (like Object Detection)
- Both can run in parallel on same frames
- No interference between modules

### 4. Spatial Analysis Feeds Obstacle Avoidance
**Why**: Bridge current and future systems
- Current system detects obstacles
- Future system uses that info for replanning
- Seamless integration

---

## 📈 Development Roadmap

### Phase 0: Current State (COMPLETE ✅)
- Object detection, tracking, spatial analysis
- Voice input/output
- Scene descriptions
- Basic testing and documentation

### Phase 1: Architecture Refactoring (1-2 days)
- Rename Navigation → Spatial Analysis
- Update all imports and references
- Document integration points
- Test everything still works

### Phase 2: Map-Based Navigation (12-19 weeks)
- **Weeks 1-6**: SLAM and localization
- **Weeks 7-9**: Path planning
- **Weeks 10-12**: Turn-by-turn guidance
- **Weeks 13-15**: Obstacle avoidance
- **Weeks 16-19**: Testing and polish

### Phase 3: Additional Sensors (4-6 weeks)
- RFID integration
- IMU integration
- WiFi positioning
- Sensor fusion

### Phase 4: Web UI (2-3 weeks)
- Complete FastAPI backend
- Build React/Vue frontend
- WebSocket streaming
- Interactive controls

---

## 🔍 Quick Reference

### Current System Capabilities
✅ Real-time object detection (80+ classes)
✅ Multi-object tracking
✅ Spatial hazard warnings ("chair on right")
✅ Voice commands (pause, resume, describe)
✅ Voice announcements
✅ Scene descriptions every 5s
✅ Webcam and video replay

### Future System Capabilities
📋 Indoor positioning (know where you are)
📋 Map-based navigation (path planning)
📋 Turn-by-turn guidance ("turn right in 5m")
📋 Multi-floor building support
📋 RFID object identification
📋 Web-based visual interface
📋 Advanced obstacle avoidance

---

## 💡 For Developers

### Adding a New Module?
1. Inherit from `BaseModule`
2. Implement `start()` method
3. Subscribe to relevant message types via ResultBus
4. Publish new message types as needed
5. Register module in app (e.g., `run_webcam_full.py`)

### Integrating Navigation?
1. Modules already exist in placeholder: `modules/navigation/`
2. Implement SLAM, Localization, Path Planning, etc.
3. Publish new message types: `UserLocation`, `PlannedRoute`, `NavigationInstruction`
4. Existing modules (Voice Output, Fusion) will automatically integrate via ResultBus

### Testing?
```bash
# Test current system
python3 run_webcam_full.py

# Run unit tests
pytest tests/

# Test specific module
pytest tests/test_spatial_analysis.py
```

---

**Last Updated**: 2025-12-27
**Version**: 1.0 (with map-based navigation architecture)

