import cv2
import mediapipe as mp
from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

# pyrefly: ignore [missing-import]
from pysimverse import Drone

# MISSION 6 - BODY FOLLOWER DRONE

print("=" * 60)
print("MISSION 6 - BODY FOLLOWER DRONE")
print("=" * 60)

# STEP 1: FIND POSE LANDMARKER MODEL
PROJECT_ROOT = Path(__file__).resolve().parent

MODEL_PATH = PROJECT_ROOT / "pose_landmarker.task"

print()
print("Looking for model at:")
print(MODEL_PATH)

# STEP 2: CHECK MODEL
if not MODEL_PATH.exists():

    print()
    print("ERROR: pose_landmarker.task was not found!")
    print()
    print("Expected location:")
    print(MODEL_PATH)

    raise SystemExit


model_size = MODEL_PATH.stat().st_size

print()
print("Model found!")
print("Model size:", model_size, "bytes")


if model_size == 0:

    print()
    print("ERROR: Model file is empty!")

    raise SystemExit

# STEP 3: CREATE MEDIAPIPE POSE LANDMARKER
print()
print("Loading MediaPipe Pose Landmarker...")


base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)


options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_poses=1,

    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


try:

    detector = vision.PoseLandmarker.create_from_options(
        options
    )

except Exception as error:

    print()
    print("ERROR: Could not initialize MediaPipe Pose Landmarker.")
    print()
    print("Error:")
    print(error)

    raise SystemExit


print()
print("MediaPipe Pose Landmarker initialized successfully!")

# STEP 4: CONNECT TO DRONE
print()
print("Connecting to drone...")


drone = Drone()

drone.connect()

time.sleep(1)


print("Drone connected successfully!")

# STEP 5: TAKE OFF
print()
print("Drone taking off...")


drone.take_off()

time.sleep(2)


print("Drone has taken off!")

# STEP 6: DRONE CONTROL SETTINGS
# Maximum movement speed
SPEED_X = 30
SPEED_Y = 30

# HORIZONTAL DEADZONE
# 0.00             0.50              1.00
# LEFT            CENTER            RIGHT
# Body left  -> drone left
# Body right -> drone right

X_LEFT_LIMIT = 0.40
X_RIGHT_LIMIT = 0.60

# VERTICAL DEADZONE
# 0.00 = TOP
# 0.50 = CENTER
# 1.00 = BOTTOM
# Body up   -> drone up
# Body down -> drone down

Y_TOP_LIMIT = 0.40
Y_BOTTOM_LIMIT = 0.60

# STEP 7: OPEN WEBCAM
print()
print("Opening webcam...")


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    try:
        drone.send_rc_control(
            0,
            0,
            0,
            0
        )

        drone.land()

    except Exception as error:

        print("Error landing drone:", error)

    detector.close()

    raise SystemExit


print("Webcam started successfully!")

# CONTROLS
print()
print("=" * 60)
print("MISSION 6 CONTROLS")
print("=" * 60)

print("BODY LEFT       -> DRONE LEFT")
print("BODY RIGHT      -> DRONE RIGHT")
print("BODY UP         -> DRONE UP")
print("BODY DOWN/BEND  -> DRONE DOWN")
print("BODY CENTER     -> DRONE HOVER")
print("NO BODY         -> DRONE HOVER")
print("PRESS Q         -> LAND AND EXIT")

print("=" * 60)

# STEP 8: MAIN LOOP
try:
    while True:
        # READ CAMERA
        success, frame = cap.read()
        if not success:
            print("ERROR: Could not read camera frame.")
            break
        # Mirror camera
        frame = cv2.flip(
            frame,
            1
        )
        # Frame dimensions
        height, width, _ = frame.shape

        # DRAW CENTER LINES
        center_x = width // 2
        center_y = height // 2

        # Horizontal center
        cv2.line(
            frame,
            (center_x, 0),
            (center_x, height),
            (0, 0, 255),
            2
        )
        # Vertical center
        cv2.line(
            frame,
            (0, center_y),
            (width, center_y),
            (0, 0, 255),
            2
        )

        # DRAW X DEADZONE
        x_left_pixel = int(
            width * X_LEFT_LIMIT
        )
        x_right_pixel = int(
            width * X_RIGHT_LIMIT
        )
        cv2.line(
            frame,
            (x_left_pixel, 0),
            (x_left_pixel, height),
            (255, 0, 0),
            1
        )
        cv2.line(
            frame,
            (x_right_pixel, 0),
            (x_right_pixel, height),
            (255, 0, 0),
            1
        )

        # DRAW Y DEADZONE
        y_top_pixel = int(
            height * Y_TOP_LIMIT
        )
        y_bottom_pixel = int(
            height * Y_BOTTOM_LIMIT
        )
        cv2.line(
            frame,
            (0, y_top_pixel),
            (width, y_top_pixel),
            (255, 0, 0),
            1
        )
        cv2.line(
            frame,
            (0, y_bottom_pixel),
            (width, y_bottom_pixel),
            (255, 0, 0),
            1
        )
        # CONVERT BGR -> RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )
       
        # CREATE MEDIAPIPE IMAGE
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )
        
        # DETECT BODY
         detection_result = detector.detect(
            mp_image
        )

        # DEFAULT DRONE COMMANDS
        left_right = 0
        forward_backward = 0
        up_down = 0
        yaw = 0
        direction_x = "CENTER"
        direction_y = "CENTER"

        # BODY DETECTED
        if detection_result.pose_landmarks:
            landmarks = detection_result.pose_landmarks[0]
            # GET SHOULDERS
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            
            # CALCULATE BODY CENTER
            body_center_x = (
                left_shoulder.x +
                right_shoulder.x
            ) / 2
            body_center_y = (
                left_shoulder.y +
                right_shoulder.y
            ) / 2
            
            # CONVERT TO PIXELS
            body_x = int(
                body_center_x * width
            )
            body_y = int(
                body_center_y * height
            )
            
            # DRAW BODY CENTER
            cv2.circle(
                frame,
                (body_x, body_y),
                15,
                (0, 255, 255),
                -1
            )
            # DRAW SHOULDER POINTS
            left_x = int(
                left_shoulder.x * width
            )
            left_y = int(
                left_shoulder.y * height
            )
            right_x = int(
                right_shoulder.x * width
            )
            right_y = int(
                right_shoulder.y * height
            )
            cv2.circle(
                frame,
                (left_x, left_y),
                8,
                (0, 255, 0),
                -1
            )
            cv2.circle(
                frame,
                (right_x, right_y),
                8,
                (0, 255, 0),
                -1
            )
   
            # HORIZONTAL MOVEMENT
            if body_center_x < X_LEFT_LIMIT:
                direction_x = "LEFT"
                left_right = -SPEED_X
            elif body_center_x > X_RIGHT_LIMIT:
                direction_x = "RIGHT"
                left_right = SPEED_X
            else:
                direction_x = "CENTER"
                left_right = 0
           
            # VERTICAL MOVEMENT      
           if body_center_y < Y_TOP_LIMIT:
                direction_y = "UP"
                up_down = SPEED_Y

            elif body_center_y > Y_BOTTOM_LIMIT:
                direction_y = "DOWN"
                up_down = -SPEED_Y
            else:
                direction_y = "CENTER"
                up_down = 0
           
            # DEBUG INFORMATION
            print(
                f"X={body_center_x:.2f} "
                f"Y={body_center_y:.2f} "
                f"X_DIR={direction_x} "
                f"Y_DIR={direction_y} "
                f"LR={left_right} "
                f"UD={up_down}"
            )
            # DISPLAY BODY POSITION
            cv2.putText(
                frame,
                f"Body X: {body_center_x:.2f}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            cv2.putText(
                frame,
                f"Body Y: {body_center_y:.2f}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            cv2.putText(
                frame,
                f"X Direction: {direction_x}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )
            cv2.putText(
                frame,
                f"Y Direction: {direction_y}",
                (20, 135),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )
        # NO BODY DETECTED
        else:
            body_center_x = None
            body_center_y = None

            direction_x = "NO BODY"
            direction_y = "NO BODY"

            left_right = 0
            forward_backward = 0
            up_down = 0
            yaw = 0
            print(
                "NO BODY -> DRONE HOVER"
            )
        
        # SEND RC CONTROL TO DRONE
        drone.send_rc_control(
            left_right,
            forward_backward,
            up_down,
            yaw
        )
       
        # DISPLAY DRONE COMMAND
        command_text = (
            f"LR: {left_right} | "
            f"UD: {up_down}"
        )
        cv2.putText(
            frame,
            command_text,
            (20, height - 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )
        
        # DISPLAY MAIN STATUS
        status = (
            f"{direction_x} | "
            f"{direction_y}"
        )
        cv2.putText(
            frame,
            status,
            (width // 2 - 150, height - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )
       
        # SHOW CAMERA
        cv2.imshow(
            "Mission 6 - Body Follower Drone",
            frame
        )
        
        # PRESS Q TO EXIT
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print()
            print("Q pressed.")
            print("Ending Mission 6...")

            break

except KeyboardInterrupt:
    print()
    print("Program interrupted by user.")

# SAFETY CLEANUP
finally:
    print()
    print("Stopping drone...")
    try:
        # Stop all movement
        drone.send_rc_control(
            0,
            0,
            0,
            0
        )
        time.sleep(0.5)
        
        # Land drone
        print("Landing drone...")
        drone.land()
        time.sleep(1)
    except Exception as error:
        print(
            "Error during drone landing:",
            error
        )
   
    # CLOSE WEBCAM
    cap.release()
    # CLOSE OPENCV
    cv2.destroyAllWindows()
   
    # CLOSE MEDIAPIPE
    detector.close()

    print()
    print("=" * 60)
    print("MISSION 6 FINISHED")
    print("=" * 60)
