# 📖 Smart Glasses Usage Guide

## Quick Start

### Option 1: Basic Mode (Visual + Text Logs)
```bash
cd /Users/ahmed/smart-glasses
python3 run_webcam.py
```

**What you get:**
- ✅ Real-time object detection (YOLO)
- ✅ Object tracking
- ✅ Navigation guidance (text)
- ✅ Scene descriptions (text, every 5s)

### Option 2: Full Mode (Visual + Voice)
```bash
cd /Users/ahmed/smart-glasses
python3 run_webcam_full.py
```

**What you get:**
- ✅ Everything from basic mode
- ✅ 🔊 Voice output (speaks announcements)
- ✅ 🎤 Voice commands (pause, resume, describe, quit)

---

## What Does It Do?

### Real-Time Detection
Points your laptop camera at objects and detects:
- **People** (you!)
- **Electronics**: laptop, phone, keyboard, mouse, tv
- **Furniture**: chair, couch, table, bed
- **Kitchen items**: cup, bottle, bowl
- **80 COCO classes total**

### Navigation Guidance
Tells you:
- **Direction**: "person on the left", "chair ahead", "cup on the right"
- **Distance**: "far", "mid", "near", "very close"
- **Movement**: "approaching", "receding", "stationary"
- **Urgency**: Low ℹ️, Medium ⚠️, High ⚠️⚠️, Critical 🚨

### Scene Descriptions (Every 5 seconds)
Summarizes what's in view:
```
🖼️  SCENE: 2 objects detected: a person ahead, a chair on the right
🖼️  SCENE: One object detected: a laptop on the desk
🖼️  SCENE: Multiple objects: a cup on the right, a mouse on the right
```

---

## How to Use

### 1. Start the System
```bash
# Basic mode (recommended for first try)
python3 run_webcam.py

# Or with voice
python3 run_webcam_full.py
```

### 2. Point Your Camera
- **At yourself**: Detects "person"
- **At your desk**: Detects laptop, mouse, keyboard, phone, cup, etc.
- **Around the room**: Detects furniture, TV, etc.

### 3. Watch the Output
The terminal shows:
```
ℹ️  Track #1: person ahead on center [center, mid, stationary]
⚠️  Track #2: laptop approaching on right [right, mid, approaching]
📢 ANNOUNCEMENT: PERSON AHEAD ON CENTER
🖼️  SCENE: 2 objects detected: a person ahead, a laptop on the right
```

### 4. Stop the System
Press **Ctrl+C** to stop

---

## Understanding the Output

### Track Lines (Real-time)
```
ℹ️  Track #1: person ahead on center [center, mid, stationary]
     └─ Emoji: ℹ️ Low, ⚠️ Medium, ⚠️⚠️ High, 🚨 Critical
            └─ Track ID: Persistent identifier
                  └─ Object: What it detected
                        └─ Direction: left/center/right
                              └─ Zone: near/mid/far
                                    └─ Movement: approaching/receding/stationary
```

### Announcements (Important Events)
```
📢 ANNOUNCEMENT: PERSON APPROACHING ON LEFT
```
Only shows when:
- Object is close AND approaching
- New object appears
- Object changes significantly

### Scene Descriptions (Periodic)
```
🖼️  SCENE: 3 objects detected: a person ahead, a cup on the right, a chair on the right
```
Every 5 seconds, summarizes all visible objects

---

## Voice Commands (Full Mode Only)

If running `run_webcam_full.py`, you can say:

| Command | What It Does |
|---------|--------------|
| **"pause"** or **"stop"** | Pauses processing |
| **"resume"** or **"play"** | Resumes processing |
| **"describe"** or **"what do you see"** | Immediate scene description |
| **"quit"** or **"exit"** | Stops the system |

---

## Save Output to File

### For Later Review
```bash
# Save everything
python3 run_webcam.py > output.log 2>&1

# Watch live AND save
python3 run_webcam.py 2>&1 | tee output.log

# With timestamp
python3 run_webcam.py 2>&1 | tee logs/run_$(date +%Y%m%d_%H%M%S).log
```

### Filter Specific Events
```bash
# Only scene descriptions
python3 run_webcam.py 2>&1 | grep "SCENE:"

# Only announcements
python3 run_webcam.py 2>&1 | grep "📢"

# Only urgent warnings
python3 run_webcam.py 2>&1 | grep -E "⚠️⚠️|🚨"
```

---

## Test Scenarios

### Scenario 1: Desk Detection
1. Start: `python3 run_webcam.py`
2. Point camera at your desk
3. Watch it detect: laptop, keyboard, mouse, cup, phone

### Scenario 2: Person Detection
1. Start the system
2. Sit in front of camera
3. Move closer → urgency increases (ℹ️ → ⚠️ → ⚠️⚠️ → 🚨)
4. Move away → "person receding"
5. Move left/right → direction changes

### Scenario 3: Multiple Objects
1. Point at cluttered desk
2. Watch it track multiple objects
3. Scene description groups them by location

### Scenario 4: Movement Detection
1. Hold an object (cup, phone)
2. Move it towards camera → "approaching"
3. Move it away → "receding"
4. Hold still → "stationary"

---

## Configuration

### Change Detection Confidence
Edit `core_platform/control_state.py`:
```python
detection_conf_threshold: float = 0.5  # Lower = more detections (may be noisy)
                                       # Higher = fewer detections (more confident)
```

### Change Scene Description Interval
Edit `run_webcam.py`:
```python
SceneDescriptionModule(description_interval=5.0)  # Change 5.0 to 10.0 for every 10s
```

### Change Camera FPS
Edit `run_webcam.py`:
```python
fps = 15  # Change to 10 (slower, less CPU) or 20 (faster, more CPU)
```

---

## Troubleshooting

### "Failed to open camera 0"
- **Solution**: Close other apps using camera (Zoom, FaceTime, etc.)

### "No detections"
- **Check**: Is camera pointed at detectable objects?
- **Try**: Lower confidence threshold to 0.3
- **Check**: Good lighting helps

### "Too many detections"
- **Solution**: Increase confidence threshold to 0.6 or 0.7

### High CPU usage
- **Solution**: Lower FPS from 15 to 10
- **Solution**: Use smaller YOLO model (already using yolov8n, the smallest)

---

## Example Session

```bash
$ python3 run_webcam.py

Starting Smart Glasses with Webcam...
Camera ID: 0, FPS: 15
Press Ctrl+C to stop

Loading YOLO detector...
✓ YOLO model loaded successfully
✓ Using YOLO detector (real ML - 80 object classes)
ObjectDetection module started using YOLO (real ML)
Tracker module started
Navigation module started
Fusion module started
SceneDescription module started (interval: 5.0s)
✓ All modules started

Opened camera 0 (640x480 @ 15 fps)

ℹ️  Track #1: laptop ahead on center [center, mid, stationary]
ℹ️  Track #2: cup right [right, far, stationary]
📢 ANNOUNCEMENT: LAPTOP AHEAD ON CENTER
🖼️  SCENE: 2 objects detected: a laptop ahead, a cup on the right

⚠️  Track #3: person approaching on left [left, mid, approaching]
📢 ANNOUNCEMENT: PERSON APPROACHING ON LEFT
🖼️  SCENE: 3 objects detected: a laptop ahead, a cup on the right, a person on the left

^C
Shutting down...
Released camera 0
Done!
```

---

## What's Next?

1. **Try it**: Start with basic mode
2. **Test objects**: Point at different things
3. **Enable voice**: Run full mode for speech
4. **Customize**: Adjust settings to your needs
5. **Deploy**: Eventually works with real smart glasses hardware!

---

Enjoy your smart glasses system! 🤓

