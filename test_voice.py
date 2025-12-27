#!/usr/bin/env python3
"""Test voice output - speaks a simple message."""

import pyttsx3

print("Testing voice output...")
print("Initializing text-to-speech engine...")

engine = pyttsx3.init()

# Set properties
engine.setProperty('rate', 175)  # Speed (words per minute)
engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# Get available voices
voices = engine.getProperty('voices')
print(f"Available voices: {len(voices)}")
for i, voice in enumerate(voices):
    print(f"  {i}: {voice.name}")

# Speak test message
print("\nSpeaking test message...")
engine.say("Hello! Voice output is working. This is the smart glasses navigation system.")
engine.say("I can describe scenes and provide navigation guidance.")
engine.runAndWait()

print("✓ Voice output test complete!")

