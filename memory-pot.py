from deepface import DeepFace
from picamera2 import Picamera2
from gpiozero import Servo, LED
from gpiozero.pins.lgpio import LGPIOFactory
import cv2
import time
from collections import deque

print("=" * 60)
print("PETGRIEF - EMOTION DETECTION SYSTEM")
print("=" * 60)

# GPIO pins
print("\n[SETUP] Initializing GPIO...")
factory = LGPIOFactory()
tail_servo = Servo(26, pin_factory=factory, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
ear_left_servo = Servo(27, pin_factory=factory, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
ear_right_servo = Servo(19, pin_factory=factory, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
head_servo = Servo(5, pin_factory=factory, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
face_led = LED(22)

# Center servos then detach
tail_servo.value = 0
ear_left_servo.value = 0
ear_right_servo.value = 0
head_servo.value = 0
time.sleep(0.3)
tail_servo.value = None
ear_left_servo.value = None
ear_right_servo.value = None
head_servo.value = None
face_led.off()
print("  ✓ Servos centered and detached, LED off")

servo_busy = False

def wag_happy():
    """Happy - TAIL ONLY wag, 4 repetitions, FAST"""
    global servo_busy
    servo_busy = True
    print("    → [ACTION] Happy wag - TAIL ONLY, 4 repetitions, FAST")
    
    angles = [0, -0.7, -1, 0.7, 1, -0.7, -1, 0.7, 1, 0]
    for rep in range(4):
        print(f"      Repetition {rep + 1}/4")
        for angle in angles:
            tail_servo.value = angle
            time.sleep(0.08)
    
    tail_servo.value = 0
    time.sleep(0.3)
    tail_servo.value = None
    print("    → [COMPLETE] Happy wag finished")
    servo_busy = False

def wag_sad():
    """Sad - both ears tilt BACKWARDS, 2 repetitions"""
    global servo_busy
    servo_busy = True
    print("    → [ACTION] Sad - both ears tilt BACKWARDS, 2 repetitions")
    
    purple_angles = [0, -0.33, 0, -0.33, 0]  # Left ear backward
    yellow_angles = [0, 0.33, 0, 0.33, 0]    # Right ear backward
    
    for rep in range(2):
        print(f"      Repetition {rep + 1}/2")
        for i in range(len(purple_angles)):
            ear_left_servo.value = purple_angles[i]
            ear_right_servo.value = yellow_angles[i]
            time.sleep(0.5)
    
    ear_left_servo.value = 0
    ear_right_servo.value = 0
    time.sleep(0.3)
    ear_left_servo.value = None
    ear_right_servo.value = None
    print("    → [COMPLETE] Sad wag finished")
    servo_busy = False

def tilt_head():
    """Head tilt - curious/neutral/surprise response"""
    global servo_busy
    servo_busy = True
    print("    → [ACTION] Head tilt - curious/neutral/surprise response")
    
    angles = [0, 0.22, 0, 0.22, 0]
    for rep in range(2):
        print(f"      Repetition {rep + 1}/2")
        for angle in angles:
            head_servo.value = angle
            time.sleep(0.25)
    
    head_servo.value = 0
    time.sleep(0.3)
    head_servo.value = None
    print("    → [COMPLETE] Head tilt finished")
    servo_busy = False

# Initialize camera
print("\n[SETUP] Initializing camera...")
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)}, buffer_count=2)
picam2.configure(preview_config)
picam2.start()
time.sleep(2)
print("  ✓ Camera ready")

# Tracking variables
emotion_history = deque(maxlen=8)
last_action_time = 0
action_cooldown = 3
frame_count = 0
led_on_until_frame = 0
face_detected_flag = False
idle_face_count = 0

print("\n" + "=" * 60)
print("SYSTEM ACTIVE - CONFIDENCE-BASED MODE")
print("Happy/Sad: High(>80%)=1, Med(60-80%)=2, Low(<60%)=3")
print("Neutral/Surprise: High/Med(>60%)=4, Low(<60%)=6")
print("Idle head tilt: 4 frames")
print("=" * 60)
print()

try:
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_count += 1
        
        if frame_count % 5 != 0:
            if frame_count < led_on_until_frame:
                if not face_detected_flag:
                    print(f"[Frame {frame_count}] LED ON")
                    face_detected_flag = True
                face_led.on()
            else:
                if face_detected_flag:
                    print(f"[Frame {frame_count}] LED OFF")
                    face_detected_flag = False
                face_led.off()
            time.sleep(0.1)
            continue
        
        if servo_busy:
            print(f"\n[Frame {frame_count}] ⚠️  SERVO MOVING - Skipping")
            time.sleep(0.1)
            continue
        
        cv2.imwrite('/tmp/current_frame.jpg', frame_bgr)
        print(f"\n[Frame {frame_count}] ━━━ ANALYZING ━━━")
        
        try:
            result = DeepFace.analyze('/tmp/current_frame.jpg', actions=['emotion'], enforce_detection=True, silent=True)
            led_on_until_frame = frame_count + 10
            
            emotion = result[0]['dominant_emotion']
            emotion_scores = result[0]['emotion']
            confidence = emotion_scores[emotion]
            
            emotion_history.append(emotion)
            
            print(f"  ✓ FACE DETECTED")
            print(f"    Current: {emotion} (confidence: {confidence:.1f}%)")
            print(f"    History: {list(emotion_history)} ({len(emotion_history)}/8)")
            
            # Determine required detections based on emotion type and confidence
            if emotion in ['happy', 'sad']:
                # Happy/Sad thresholds (fast response)
                if confidence > 80:
                    required = 1
                    threshold_type = "HIGH"
                elif confidence > 60:
                    required = 2
                    threshold_type = "MEDIUM"
                else:
                    required = 3
                    threshold_type = "LOW"
            elif emotion in ['neutral', 'surprise']:
                # Neutral/Surprise thresholds (need more confirmation)
                if confidence > 60:
                    required = 4
                    threshold_type = "HIGH/MEDIUM"
                else:
                    required = 6
                    threshold_type = "LOW"
            else:
                # Other emotions (angry, fear, disgust) - count toward idle
                required = 999  # Won't trigger
                threshold_type = "N/A"
            
            print(f"    Confidence level: {threshold_type} (need {required} detections)")
            
            if len(emotion_history) >= required and required < 999:
                dominant = max(set(emotion_history), key=emotion_history.count)
                count = emotion_history.count(dominant)
                
                print(f"    Dominant: {dominant} ({count}/{len(emotion_history)})")
                
                time_since_last = time.time() - last_action_time
                print(f"    Time since last: {time_since_last:.1f}s")
                
                if time_since_last > action_cooldown:
                    if dominant == 'happy':
                        print(f"  ★ TRIGGERING: Happy (4x wag)")
                        wag_happy()
                        last_action_time = time.time()
                        idle_face_count = 0
                    elif dominant == 'sad':
                        print(f"  ★ TRIGGERING: Sad (ears backward)")
                        wag_sad()
                        last_action_time = time.time()
                        idle_face_count = 0
                    elif dominant in ['neutral', 'surprise']:
                        print(f"  ★ TRIGGERING: Head tilt ({dominant})")
                        tilt_head()
                        last_action_time = time.time()
                        idle_face_count = 0
                else:
                    remaining = action_cooldown - time_since_last
                    print(f"    ⏳ Cooldown: {remaining:.1f}s")
                    idle_face_count += 1
                    print(f"    Idle: {idle_face_count}/4")
                    if idle_face_count >= 4:
                        print(f"  ★ TRIGGERING: Head tilt (idle)")
                        tilt_head()
                        idle_face_count = 0
            else:
                if required < 999:
                    needed = required - len(emotion_history)
                    print(f"    ⏳ Need {needed} more")
                else:
                    # Other emotions count toward idle
                    idle_face_count += 1
                    print(f"    Other emotion - Idle: {idle_face_count}/4")
                    if idle_face_count >= 4:
                        print(f"  ★ TRIGGERING: Head tilt (idle)")
                        tilt_head()
                        idle_face_count = 0
        
        except:
            print(f"  ✗ NO FACE")
            if len(emotion_history) > 0:
                emotion_history.clear()
            idle_face_count = 0
        
        if frame_count < led_on_until_frame:
            face_led.on()
        else:
            face_led.off()
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nSHUTTING DOWN")

finally:
    picam2.stop()
    tail_servo.value = 0
    ear_left_servo.value = 0
    ear_right_servo.value = 0
    head_servo.value = 0
    time.sleep(0.3)
    tail_servo.value = None
    ear_left_servo.value = None
    ear_right_servo.value = None
    head_servo.value = None
    face_led.off()
    print("  ✓ Stopped")