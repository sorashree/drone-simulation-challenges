import cv2
import mediapipe as mp
from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
# pyrefly: ignore [missing-import]
from pysimverse import Drone
import time

# MISSION 3 - HAND LEFT / RIGHT DETECTION & DRONE CONTROL
print("=" * 60)
print("MISSION 3 - HAND LEFT / RIGHT DETECTION & DRONE CONTROL")
print("=" * 60)

# FIND PROJECT PATH AND MODEL
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "hand_landmarker.task"

# Fallback in case the script is placed or run in a template subdirectory
if not MODEL_PATH.exists():
    MODEL_PATH = PROJECT_ROOT.parent / "hand_landmarker.task"

print(f"Looking for MediaPipe model at: {MODEL_PATH}")

# CHECK IF MODEL EXISTS
if not MODEL_PATH.exists():
    print("ERROR: hand_landmarker.task was not found!")
    print(f"Expected location: {MODEL_PATH}")
    exit()

model_size = MODEL_PATH.stat().st_size
print(f"Model found! Size: {model_size} bytes")

if model_size == 0:
    print("ERROR: The model file is empty!")
    exit()

# CREATE MEDIAPIPE HAND LANDMARKER
print("Loading MediaPipe Hand Landmarker...")

base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,  # Track only one hand as requested
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

try:
    detector = vision.HandLandmarker.create_from_options(options)
except Exception as e:
    print("ERROR: Could not load MediaPipe model.")
    print(e)
    exit()

print("MediaPipe Hand Landmarker loaded successfully!")
print()


# INITIALIZE AND CONNECT DRONE
print("Connecting to drone...")
drone = Drone()
drone.connect()
time.sleep(1)

print("Drone taking off...")
drone.take_off()
time.sleep(1)

SPEED = 30


# MISSION INSTRUCTIONS
print("=" * 60)
print("MISSION 3 CONTROLS")
print("=" * 60)
print("Move your hand to the LEFT side  -> Drone moves LEFT")
print("Move your hand to the RIGHT side -> Drone moves RIGHT")
print("Keep your hand in the CENTER     -> Drone STOPS")
print("Remove your hand                 -> Drone STOPS")
print("Press Q in the window to quit.")
print("=" * 60)
print()

# OPEN WEBCAM
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    try:
        drone.send_rc_control(0, 0, 0, 0)
        drone.land()
    except Exception as e:
        print(f"Error landing drone: {e}")
    detector.close()
    exit()

print("Camera started!")
print()

# Keep track of the last printed direction to avoid spamming the console
last_printed_direction = None


# MAIN LOOP
try:
    while True:
        success, frame = cap.read()
        if not success:
            print("ERROR: Could not read camera frame.")
            break

        # Flip the frame horizontally to behave like a mirror
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # CREATE LEFT / DEADZONE / RIGHT AREAS
        # Left boundary: 35% of width
        # Right boundary: 65% of width
        # Deadzone is in the center (35% to 65%)
        deadzone_left = int(width * 0.35)
        deadzone_right = int(width * 0.65)

        # Draw partition lines (boundaries of the deadzone)
        cv2.line(frame, (deadzone_left, 0), (deadzone_left, height), (0, 0, 255), 2)
        cv2.line(frame, (deadzone_right, 0), (deadzone_right, height), (0, 0, 255), 2)

        # Label regions on the display window
        cv2.putText(frame, "LEFT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, "DEADZONE", (width // 2 - 80, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, "RIGHT", (width - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convert frame to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect hand landmarks
        detection_result = detector.detect(mp_image)
        direction = "NO HAND"

        if detection_result.hand_landmarks:
            # We only track one hand
            hand_landmarks = detection_result.hand_landmarks[0]
            
            # Use wrist (landmark 0) as hand position reference
            wrist = hand_landmarks[0]
            hand_x = int(wrist.x * width)
            hand_y = int(wrist.y * height)

            # Draw a circle on the wrist position
            cv2.circle(frame, (hand_x, hand_y), 15, (0, 255, 255), -1)

            # Draw the wrist coordinates
            cv2.putText(frame, f"Hand X: {hand_x}", (20, height - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Check which partition the hand is in
            if hand_x < deadzone_left:
                direction = "LEFT"
            elif hand_x > deadzone_right:
                direction = "RIGHT"
            else:
                direction = "DEADZONE"

        # Print direction to console if it changed
        if direction != last_printed_direction:
            print(f"Hand state: {direction}")
            last_printed_direction = direction

        # Determine left/right movement speed based on direction
        if direction == "LEFT":
            left_right = -SPEED
        elif direction == "RIGHT":
            left_right = SPEED
        else:  # DEADZONE or NO HAND
            left_right = 0

        # Send RC command to drone
        drone.send_rc_control(left_right, 0, 0, 0)

        # Display the current direction on frame
        cv2.putText(frame, direction, (width // 2 - 100, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        # Show the live feed
        cv2.imshow("Mission 3 - Hand Direction", frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Quitting...")
            break

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")

finally:
    # Cleanup and land the drone safely
    print("Landing drone...")
    try:
        drone.send_rc_control(0, 0, 0, 0)
        time.sleep(0.5)
        drone.land()
        time.sleep(1)
    except Exception as e:
        print(f"Error during drone landing/cleanup: {e}")

    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("Mission 3 finished.")
