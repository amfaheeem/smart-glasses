# 📹 Using Webcam with Smart Glasses Pipeline

## Quick Start

```bash
cd /Users/ahmed/smart-glasses
PYTHONPATH=. python3 run_webcam.py
```

That's it! Point your laptop camera at objects and watch the real-time announcements.

---

## What You'll See

The terminal will show:
- ℹ️ **Low urgency**: Objects detected far away
- ⚠️ **Medium urgency**: Objects approaching
- ⚠️⚠️ **High urgency**: Objects nearby
- 🚨 **Critical**: Objects very close and approaching!
- 📢 **Announcements**: Final fusion decisions with cooldown

Example output:
```
ℹ️  Track #1: door detected right [right, far, stationary]
⚠️  Track #2: person approaching on left [left, mid, approaching]
📢 PERSON APPROACHING ON LEFT [object]
🚨 Track #2: person very close, left [left, near, approaching]
```

---

## Camera Settings

Default settings (in `run_webcam.py`):
- **Camera ID**: 0 (default webcam)
- **FPS**: 15 (optimized for real-time)
- **Resolution**: 640x480

### Change Camera

If you have multiple cameras:
```python
camera_id = 0  # Built-in webcam
camera_id = 1  # External USB camera
```

### Adjust Performance

For faster processing:
```python
fps = 10  # Lower FPS = less CPU
width = 320
height = 240
```

For better quality:
```python
fps = 20  # Higher FPS = smoother
width = 1280
height = 720
```

---

## Webcam vs Video File

| Feature | Webcam | Video File |
|---------|--------|------------|
| **Real-time** | ✅ Yes | ❌ No (replay) |
| **Speed control** | ❌ Fixed FPS | ✅ 0.5x - 2x |
| **Pause/Resume** | ✅ Yes | ✅ Yes |
| **Reproducible** | ❌ No | ✅ Yes |
| **Best for** | Live demo | Testing/debugging |

---

## Controls

While running:
- **Ctrl+C**: Stop gracefully
- Camera permission dialog may appear on first run

---

## Troubleshooting

### "Failed to open camera 0"

**Cause**: Camera in use or no permission

**Solutions**:
1. Close other apps using the camera (Zoom, FaceTime, etc.)
2. Grant camera permission in System Preferences
3. Try a different camera ID: `camera_id = 1`

### "No module named 'cv2'"

**Solution**:
```bash
pip3 install opencv-python
```

### High CPU usage

**Solution**: Lower FPS
```python
fps = 10  # In run_webcam.py
```

### Camera resolution not supported

Some cameras don't support all resolutions. Try:
```python
width = 640
height = 480  # Most compatible
```

---

## Testing Without Moving

If you want to test without moving objects:

1. **Point at static objects**: Door, wall, furniture
2. **Move the laptop**: Objects will appear to move
3. **Wave your hand**: Quick test of detection
4. **Walk in front**: Test person detection

---

## Advanced: Test Different Scenarios

### Test "approaching" detection:
1. Start far from camera
2. Walk slowly towards it
3. Watch urgency increase: low → medium → high → critical

### Test "stationary" detection:
1. Stand still in frame
2. Objects should be marked as stationary

### Test "receding" detection:
1. Start close to camera
2. Walk backwards
3. Objects marked as receding

### Test direction classification:
1. Move left: Objects on "right"
2. Move right: Objects on "left"
3. Center: Objects "center"

---

## Performance Tips

1. **Close other apps** using the camera
2. **Good lighting** helps detection
3. **Lower FPS** if lagging (try fps=10)
4. **Smaller resolution** for faster processing

---

## Next Steps

Once webcam works, you can:

1. **Replace stub detector** with YOLO for real object detection
2. **Add display window** to see video + overlays
3. **Add TTS** to hear announcements
4. **Add haptic feedback** for urgency levels
5. **Deploy to smart glasses** hardware

---

## Comparison Commands

```bash
# Replay from file (testing)
PYTHONPATH=. python3 test_pipeline.py

# Live webcam (demo)
PYTHONPATH=. python3 run_webcam.py

# Run tests
PYTHONPATH=. python3 -m pytest tests/ -v
```

---

## What's Detected?

Remember: Using **stub detector** by default (deterministic patterns).

**Stub detector generates**:
- "person" objects every 3 frames
- "door" objects (always present)
- "obstacle" objects (periodic)

**For real detection**, replace with YOLO/Detectron2 in:
`modules/object_detection/module.py`

---

Enjoy testing with your webcam! 📹

