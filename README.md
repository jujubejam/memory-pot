# Memory Pot - Emotion-Detecting Robotic Plant Pot

An interactive plant pot that detects human emotions using computer vision and responds with physical movements. Built with Raspberry Pi 5, servos, and DeepFace AI for emotion recognition.

<img src="/README-image/111A5136 2.JPG" alt="Not Clicked" height="300"> <!-- Add your demo gif/image here -->

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
```
Servos (powered by 4x AA batteries):
  Battery (+) → All servo VCC (red wires)
  Battery (-) → All servo GND (brown wires) + Pi GND
  
  GPIO 26 → Tail servo signal (orange)
  GPIO 27 → Left ear servo signal (purple)
  GPIO 19 → Right ear servo signal (yellow)
  GPIO 5  → Head servo signal (blue)

LED:
  GPIO 22 → 220Ω resistor → LED (+)
  LED (-) → GND
```

## Software Requirements

- Raspberry Pi OS (64-bit recommended)
- Python 3.11+
- DeepFace
- TensorFlow
- OpenCV
- Picamera2
- gpiozero with lgpio

## Installation

### 1. System Setup
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system packages
sudo apt-get install -y python3-full python3-venv python3-picamera2 python3-libcamera
```

### 2. Create Virtual Environment
```bash
# Create virtual environment with system packages
python3 -m venv ~/petgrief --system-site-packages

# Activate environment
source ~/petgrief/bin/activate

# Create alias for easy activation (optional)
echo "alias petgrief='source ~/petgrief/bin/activate'" >> ~/.bashrc
source ~/.bashrc
```

### 3. Install Python Dependencies
```bash
# Activate virtual environment
source ~/petgrief/bin/activate

# Install packages
pip install --upgrade pip
pip install numpy pandas opencv-python tensorflow deepface gpiozero pigpio tf-keras
```

### 4. Install pigpio (for servo control)
```bash
cd ~
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
sudo pigpiod
```

### 5. Download PetGrief Code
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/petgrief.git
cd petgrief
```

### 6. Set Up Auto-Start (Optional)
```bash
sudo nano /etc/systemd/system/petgrief.service
```

Paste:
```ini
[Unit]
Description=PetGrief Emotion Detection System
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME
ExecStart=/home/YOUR_USERNAME/petgrief/bin/python3 /home/YOUR_USERNAME/petgrief_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable auto-start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable petgrief.service
sudo systemctl start petgrief.service
```

## Usage

### Manual Start
```bash
source ~/petgrief/bin/activate
python3 petgrief_main.py
```

### Auto-Start (after setup)
Just power on the Raspberry Pi - PetGrief starts automatically!

### Interacting with PetGrief

1. **Show your face** - Position yourself 1-3 feet from the camera
2. **Express emotions** - The LED lights up when your face is detected
3. **Watch responses** - PetGrief responds within 0.2-1 second based on emotion clarity
4. **Wait 3 seconds** between reactions for the cooldown period

## How It Works

### Detection Algorithm

PetGrief uses a **confidence-based detection system**:

- **High confidence (>80%)**: 1 detection needed (~0.15s response)
- **Medium confidence (60-80%)**: 2 detections needed (~0.3s response)  
- **Low confidence (<60%)**: 3-6 detections needed (~0.5-1s response)

For neutral/surprise emotions, more detections are required (4-6) to avoid false positives.

### Emotion Responses

| Emotion | Servo Action | Details |
|---------|-------------|---------|
| Happy 😊 | Tail wag | 4 repetitions, fast movement |
| Sad 😢 | Ears backward | 2 repetitions, gentle movement |
| Neutral 😐 | Head tilt | 2 repetitions, curious gesture |
| Surprise 😲 | Head tilt | 2 repetitions, curious gesture |
| No clear emotion | Head tilt | After 4 idle detections (~0.7s) |

## Configuration

### Adjusting Sensitivity

Edit `petgrief_main.py` to modify:
```python
# Confidence thresholds (line ~150)
if confidence > 80:
    required = 1  # High confidence
elif confidence > 60:
    required = 2  # Medium confidence
else:
    required = 3  # Low confidence

# Cooldown between actions (line ~93)
action_cooldown = 3  # seconds

# Idle detection threshold (line ~96)
idle_face_count = 4  # frames
```

### Customizing Movements

Modify servo movement patterns in the function definitions:
```python
# Happy tail wag (line ~36)
angles = [0, -0.7, -1, 0.7, 1, -0.7, -1, 0.7, 1, 0]
for rep in range(4):  # Number of repetitions

# Sad ear movement (line ~52)
purple_angles = [0, -0.33, 0, -0.33, 0]  # Left ear
yellow_angles = [0, 0.33, 0, 0.33, 0]   # Right ear
```

## Utility Scripts

### Center All Servos
```bash
python3 center_servos.py
```

### Test Individual Components
```bash
python3 test_camera.py  # Test camera and emotion detection
python3 test_led.py     # Test LED
python3 test_tail.py    # Test tail servo
python3 test_ears.py    # Test ear servos
python3 test_blue.py    # Test head servo
```

## Troubleshooting

### Camera not detected
```bash
# Check camera connection
rpicam-hello --list-cameras

# If not detected, check ribbon cable connection
# Blue side should face USB/Ethernet ports
```

### Servos jittering
- Check battery voltage (should be ~6V)
- Ensure ground is shared between Pi and battery pack
- Verify `servo.value = None` is called after movements

### Poor emotion detection
- Ensure good lighting on face
- Stay 1-3 feet from camera
- Make clear, exaggerated expressions
- Adjust confidence thresholds in code

### Auto-start not working
```bash
# Check service status
sudo systemctl status petgrief.service

# View logs
sudo journalctl -u petgrief.service -n 50
```

## Project Structure
```
petgrief/
├── petgrief_main.py        # Main application code
├── center_servos.py        # Utility to center all servos
├── test_camera.py          # Camera and emotion detection test
├── test_led.py            # LED test
├── test_tail.py           # Tail servo test
├── test_ears.py           # Ear servos test
├── test_blue.py           # Head servo test
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## Credits

- **Developer**: Juju
- **Framework**: DeepFace for emotion recognition
- **Hardware**: Raspberry Pi 5
- **Date**: December 2024

## License

MIT License - feel free to use and modify for your own projects!

## Acknowledgments

- DeepFace library for emotion detection
- Anthropic's Claude for development assistance
- SVA IxD program

---

**Made with ❤️ for my puppy, MingKi**