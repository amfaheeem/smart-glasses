#!/usr/bin/env python3
"""Test voice input - recognizes speech."""

import speech_recognition as sr

print("Testing voice input...")
print("Setting up microphone...")

recognizer = sr.Recognizer()
microphone = sr.Microphone()

print("Calibrating for ambient noise...")
with microphone as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)

print("\n✓ Voice input ready!")
print("\nSay something (you have 5 seconds)...")

try:
    with microphone as source:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
    
    print("Recognizing...")
    text = recognizer.recognize_google(audio)
    print(f"\n✓ You said: '{text}'")
    print("\nVoice commands are working! 🎤")
    
except sr.WaitTimeoutError:
    print("\n✗ No speech detected (timeout)")
except sr.UnknownValueError:
    print("\n✗ Could not understand audio")
except sr.RequestError as e:
    print(f"\n✗ Recognition error: {e}")
except Exception as e:
    print(f"\n✗ Error: {e}")

