# PetGrief - Emotion-Detecting Robotic Pet

An interactive robotic pet that detects human emotions using computer vision and responds with physical movements. Built with Raspberry Pi 5, servos, and DeepFace AI for emotion recognition.

![PetGrief Demo](demo.gif) <!-- Add your demo gif/image here -->

## Features

- **Real-time emotion detection** using camera and DeepFace AI
- **Physical responses** based on detected emotions:
  - 😊 **Happy** → Tail wags enthusiastically
  - 😢 **Sad** → Ears tilt backwards gently
  - 😐 **Neutral/Surprised** → Head tilts curiously
- **Confidence-based detection** for faster, smarter responses
- **Fully autonomous** - no WiFi required, works standalone
- **Auto-starts on boot** - just plug in and it works

## Hardware Requirements

### Components
- Raspberry Pi 5 (4GB+ recommended)
- Raspberry Pi Camera Module 3 (IMX708)
- 4x Micro servos:
  - 1x Tail servo (GPIO 26)
  - 2x Ear servos (GPIO 27, 19)
  - 1x Head servo (GPIO 5)
- 1x LED (GPIO 22) with 220Ω resistor
- 4x AA battery pack (6V) for servos
- Breadboard and jumper wires

### Wiring Diagram
