# Voice & Scene Description Integration Guide

## Quick Summary

I've added **3 new first-class modules** to the architecture:

1. ✅ **SceneDescriptionModule** - Generates periodic scene summaries
2. ✅ **VoiceInputModule** - Speech recognition for commands  
3. ✅ **VoiceOutputModule** - Text-to-speech for announcements

All integrate cleanly via the existing bus architecture!

---

## Architecture Decisions

### Q: Should scene description be part of object detection?
**A: No, separate module** ✓

**Why?**
- Different purpose: Aggregates vs detects
- Different timing: Periodic vs real-time
- Reuses TrackUpdate data (no duplication)
- Can be toggled independently

### Q: How do voice modules fit?
**A: As independent I/O modules** ✓

- **VoiceInput** = Input source (like camera)
- **VoiceOutput** = Output sink (like web UI)
- Both use existing ResultBus
- No changes to core pipeline needed

---

## Installation

```bash
cd /Users/ahmed/smart-glasses

# For voice input (speech recognition)
pip3 install SpeechRecognition pyaudio

# For voice output (text-to-speech)
pip3 install pyttsx3
```

---

## Usage

### Option 1: Scene Description Only (No Voice)

```python
modules = [
    ObjectDetectionModule(),
    TrackerModule(),
    NavigationModule(),
    FusionModule(),
    SceneDescriptionModule(description_interval=5.0),  # NEW!
]
```

**Output every 5 seconds:**
```
🖼️  SCENE: 2 objects detected: a person ahead, a chair on the right
```

### Option 2: Full Voice Experience

```bash
python3 run_webcam_full.py
```

**Features:**
- 🔊 Speaks announcements ("Person approaching on left")
- 🔊 Speaks scene descriptions every 5s
- 🎤 Voice commands: "pause", "resume", "describe", "quit"

---

## Data Flow

### Scene Description Flow:

```
TrackUpdate (from Tracker)
    ↓
SceneDescriptionModule
    • Maintains active tracks
    • Groups by direction & zone  
    • Every 5s, generates text
    ↓
SceneDescription event
    ↓
VoiceOutputModule → 🔊 Speech
```

### Voice Command Flow:

```
Microphone
    ↓
VoiceInputModule
    • Recognizes speech
    • Parses command
    ↓
ControlEvent (e.g., "pause")
    ↓
All modules react
```

### Voice Output Flow:

```
FusionAnnouncement + SceneDescription
    ↓
VoiceOutputModule
    • Queues text
    • TTS in background thread
    ↓
🔊 Speaker
```

---

## Example Outputs

### Scene Descriptions:
- "One object detected: a person ahead"
- "3 objects detected: a laptop ahead, a cup on the right, a chair on the right"
- "Multiple objects: 2 people on the left, laptop and cup on desk ahead"
- "Clear path. Cell phone detected on the right"

### Voice Commands:
- User says "pause" → System pauses
- User says "describe" → Immediate scene description
- User says "resume" → System resumes
- User says "quit" → System shuts down

---

## Configuration

### Scene Description:
```python
SceneDescriptionModule(
    description_interval=5.0  # Seconds between descriptions
)
```

### Voice Input:
```python
VoiceInputModule(
    enabled=True,
    language="en-US",  # or "ar-SA" for Arabic
    timeout=5.0  # Listen timeout
)
```

### Voice Output:
```python
VoiceOutputModule(
    enabled=True,
    rate=175,  # Words per minute (150-200 typical)
    volume=0.9,  # 0.0 to 1.0
    voice_gender="female"  # or "male"
)
```

---

## Integration with Existing Code

### No Changes Needed To:
- ✅ ObjectDetectionModule
- ✅ TrackerModule  
- ✅ NavigationModule
- ✅ FusionModule
- ✅ FrameBus / ResultBus

### Just Add:
```python
from modules.scene_description import SceneDescriptionModule
from modules.voice_input import VoiceInputModule
from modules.voice_output import VoiceOutputModule

# Add to modules list
modules.append(SceneDescriptionModule())
modules.append(VoiceInputModule(enabled=True))
modules.append(VoiceOutputModule(enabled=True))
```

That's it! The bus architecture handles everything.

---

## Files Created:

```
modules/
├── scene_description/
│   ├── __init__.py
│   └── module.py        ← Scene aggregation & description
├── voice_input/
│   ├── __init__.py
│   └── module.py        ← Speech recognition
└── voice_output/
    ├── __init__.py
    └── module.py        ← Text-to-speech

contracts/
└── schemas.py           ← Updated with SceneDescription

docs/
└── extended_architecture.md  ← Full architecture diagram

run_webcam_full.py       ← Demo with all features
```

---

## Testing

### Test Scene Description:
```bash
# Run with scene descriptions but no voice
python3 run_webcam.py  # Then manually add SceneDescriptionModule
```

### Test Voice Output:
```bash
# Speaks announcements
python3 run_webcam_full.py
```

### Test Voice Input:
```bash
# Say "pause" to test
python3 run_webcam_full.py
# Wait for "Listening for command..." then speak
```

---

## Benefits

1. **Modularity** - Each feature is independent
2. **Extensibility** - Easy to add more voice commands
3. **Testability** - Each module can be tested alone
4. **Flexibility** - Mix and match features
5. **Clean** - No changes to existing pipeline

---

## Next Steps

1. Install dependencies:
   ```bash
   pip3 install SpeechRecognition pyaudio pyttsx3
   ```

2. Try it:
   ```bash
   python3 run_webcam_full.py
   ```

3. Customize voice/scene settings as needed!

---

See `docs/extended_architecture.md` for full technical details!

