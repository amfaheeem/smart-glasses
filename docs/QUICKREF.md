# Quick Reference Card

## 🚀 Essential Commands

### Setup (One-Time)
```bash
cd /Users/ahmed/smart-glasses
./setup.sh
```

### Generate Sample Video
```bash
cd /Users/ahmed/smart-glasses
PYTHONPATH=. python3 apps/generate_sample.py
```

### Run Pipeline
```bash
cd /Users/ahmed/smart-glasses
PYTHONPATH=. python3 apps/run_replay.py
```

### Run Tests
```bash
cd /Users/ahmed/smart-glasses
PYTHONPATH=. python3 -m pytest tests/ -v
```

---

## 🎛️ Command Options

### Generate Sample
```bash
# Custom duration
python3 apps/generate_sample.py --duration 30 --fps 15

# High resolution
python3 apps/generate_sample.py --width 1280 --height 720

# Custom output
python3 apps/generate_sample.py --output ~/videos/
```

### Run Replay
```bash
# Custom video
python3 apps/run_replay.py --video ~/my_video.mp4

# Frame directory
python3 apps/run_replay.py --video data/samples/sample_frames/

# Custom port
python3 apps/run_replay.py --host 0.0.0.0 --port 8080

# Disable auto-generation
python3 apps/run_replay.py --no-auto-generate
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_tracker.py -v

# With coverage
pytest --cov=. tests/
```

---

## 🌐 Web UI

**URL**: http://localhost:8000

**Controls**:
- Play/Pause buttons
- Speed: 0.5x, 1x, 2x
- Detection confidence: 0-1
- Tracker IoU: 0-1
- Fusion cooldown: 0-10s

**Event Feed**:
- 🔵 Detection (blue)
- 🟢 Track (green)
- 🟠 Navigation (orange)
- 🟣 Announcement (purple)

---

## 🐛 Quick Fixes

### ModuleNotFoundError: cv2
```bash
pip3 install opencv-python
```

### ModuleNotFoundError: fastapi
```bash
pip3 install fastapi uvicorn pydantic websockets
```

### Port already in use
```bash
python3 apps/run_replay.py --port 8080
```

### WebSocket connection failed
- Check if server is running
- Refresh browser (Ctrl+Shift+R)
- Check browser console (F12)

---

## 📂 Important Files

**Entry Points**:
- `apps/run_replay.py` - Main application
- `apps/generate_sample.py` - Sample generator
- `setup.sh` - Automated setup

**Configuration**:
- `pyproject.toml` - Dependencies
- `platform/control_state.py` - Default thresholds

**Documentation**:
- `README.md` - Quick start
- `INSTALL.md` - Detailed installation
- `docs/architecture.md` - System design
- `docs/message_contracts.md` - API reference
- `docs/running.md` - Usage guide

**Tests**:
- `tests/test_buses.py` - Bus tests
- `tests/test_tracker.py` - Tracker tests
- `tests/test_navigation.py` - Navigation tests
- `tests/test_end_to_end_replay.py` - Integration tests

---

## 🔧 Module Locations

**Core Modules**:
- `modules/object_detection/` - Detection module
- `modules/tracker/` - Tracking module
- `modules/navigation/` - Navigation module
- `modules/fusion/` - Fusion module

**Platform**:
- `platform/frame_bus.py` - Frame pub-sub
- `platform/result_bus.py` - Result pub-sub
- `platform/control_state.py` - Shared state

**UI**:
- `ui/server.py` - FastAPI backend
- `ui/static/` - HTML/JS/CSS

---

## 📊 Expected Outputs

### Generate Sample
```
INFO - Generating 300 frames...
INFO - Generated MP4: data/samples/sample.mp4
INFO - Generated frame directory: data/samples/sample_frames
```

### Run Pipeline
```
INFO - ObjectDetection module started
INFO - Tracker module started
INFO - Navigation module started
INFO - Fusion module started
INFO - ✓ System started - UI available at http://127.0.0.1:8000
```

### Run Tests
```
============== 15 passed in 3.5s ==============
```

---

## 🎯 Sample Video Content

**Objects in sample.mp4**:
- Person (blue rectangle) - moves left→right
- Door (green rectangle) - stationary
- Obstacle (red circle) - approaches (grows)
- Person #2 (cyan rectangle) - enters from right
- Hazard (orange) - brief appearance

**Duration**: 10 seconds @ 30 FPS (300 frames)

---

## 🔍 Debugging

### Enable debug logging
Edit `apps/run_replay.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

### Check module status
Look for these in console:
```
INFO - ObjectDetection module started
INFO - Tracker module started
INFO - Navigation module started
INFO - Fusion module started
```

### Inspect WebSocket
Browser console (F12) should show:
```javascript
WebSocket connected
```

### Check sample video
```bash
ls -lh data/samples/sample.mp4
ls -lh data/samples/sample_frames/
```

---

## 💡 Pro Tips

1. **Lower detection threshold** if you don't see boxes (try 0.3)
2. **Increase cooldown** if too many announcements (try 5-10s)
3. **Reduce resolution** for Raspberry Pi (320x240 @ 15fps)
4. **Use frame directory** for easier debugging (inspect individual JPEGs)
5. **Check browser console** for frontend errors
6. **Check terminal output** for backend errors

---

## 🚀 Quick Demo Flow

```bash
# 1. Setup (one time)
./setup.sh

# 2. Start pipeline
PYTHONPATH=. python3 apps/run_replay.py

# 3. Open browser
# http://localhost:8000

# 4. Watch it work!
# - Frames playing
# - Boxes appearing
# - Event feed updating
# - Adjust thresholds live

# 5. Stop with Ctrl+C
```

---

## 📖 More Help

- Full docs: See `docs/` folder
- Installation: See `INSTALL.md`
- Architecture: See `docs/architecture.md`
- API reference: See `docs/message_contracts.md`

---

**Need more help?** Check `IMPLEMENTATION_COMPLETE.md` for full details.

