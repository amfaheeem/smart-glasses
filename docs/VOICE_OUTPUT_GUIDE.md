# 🔊 Voice Output Guide

## ✅ Voice Output is Now Working!

I've successfully installed `pyttsx3` and tested it. You have **177 voices** available!

---

## How to Use Voice Output

### Option 1: Run with Voice Output Enabled

```bash
cd /Users/ahmed/smart-glasses
python3 run_webcam_full.py
```

This will:
- 🔊 **Speak announcements**: "Person approaching on left"
- 🔊 **Speak scene descriptions** (every 5 seconds): "Two objects detected: a person ahead and a chair on the right"

### Option 2: Test Voice Only

```bash
python3 test_voice.py
```

Speaks: "Hello! Voice output is working..."

---

## Configure Voice Settings

Edit `run_webcam_full.py` and change the `VoiceOutputModule` parameters:

```python
VoiceOutputModule(
    enabled=True,
    rate=175,  # Speed: 150-200 recommended (words per minute)
    volume=0.9,  # Volume: 0.0 to 1.0
    voice_gender="female"  # or "male"
)
```

### Change Voice

You have many voices! Popular ones:
- **Samantha** (female, clear) - Default on macOS
- **Alex** (male, clear)
- **Daniel** (male, British)
- **Karen** (female, Australian)
- **Moira** (female, Irish)

To use a specific voice, modify `modules/voice_output/module.py`:

```python
# Around line 64, replace voice selection with:
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
# Or for Alex:
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.alex')
```

---

## What Gets Spoken?

### 1. Fusion Announcements (High Priority)
```
🔊 "Person approaching on left"
🔊 "Chair detected right"
🔊 "Obstacle very close, center"
```

### 2. Scene Descriptions (Every 5 seconds)
```
🔊 "Two objects detected: a person ahead, a chair on the right"
🔊 "One object detected: a laptop on the desk ahead"
🔊 "Multiple objects: three people on the left, tv and couch on the right"
```

---

## Run Now!

```bash
cd /Users/ahmed/smart-glasses
python3 run_webcam_full.py
```

**You'll hear:**
- Real-time announcements as objects are detected
- Scene summaries every 5 seconds
- All navigation guidance spoken aloud

---

## Adjust Speed/Volume

If voice is too fast/slow or quiet/loud, edit these values:

```python
# In run_webcam_full.py, find VoiceOutputModule and change:
rate=150,     # Slower (default: 175)
volume=1.0,   # Louder (default: 0.9)
```

Or add custom settings:

```python
VoiceOutputModule(
    enabled=True,
    rate=160,      # Comfortable speed
    volume=0.95,   # Slightly louder
    voice_gender="female"
)
```

---

## Disable Voice Output

If you want visual only (no speech):

```python
VoiceOutputModule(enabled=False)
```

Or just use `run_webcam.py` instead of `run_webcam_full.py`

---

## Test Different Voices

Create a quick test:

```python
import pyttsx3
engine = pyttsx3.init()

# Try different voices
voices = engine.getProperty('voices')
for voice in voices[:10]:  # Test first 10
    engine.setProperty('voice', voice.id)
    engine.say(f"Hello, I am {voice.name}")
    engine.runAndWait()
```

---

## Example: Multilingual

Want Arabic voice?

```python
# Look for Arabic voices in the list
# Then set:
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.maged')  # Arabic (Saudi)
```

---

Ready to hear your smart glasses talk! 🔊

