import cv2
import mediapipe as mp

from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# BODY FOLLOWER USING MEDIAPIPE POSE LANDMARKER
print("=" * 60)
print("MEDIAPIPE BODY FOLLOWER")
print("=" * 60)

# STEP 1: FIND THE MEDIAPIPE POSE LANDMARKER MODEL
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "pose_landmarker.task"

print("Looking for model at:")
print(MODEL_PATH)

# CHECK IF MODEL EXISTS
if not MODEL_PATH.exists():
    print()
    print("ERROR: pose_landmarker.task was not found!")
    print()
    print("Please put the real MediaPipe Pose Landmarker model file here:")
    print(MODEL_PATH)
    print()
    print("Do not create an empty file manually.")
    print("=" * 60)

    exit()

# CHECK MODEL FILE SIZE
model_size = MODEL_PATH.stat().st_size

print("Model found!")
print("Model size:", model_size, "bytes")

# Check if the file is empty
if model_size == 0:
    print()
    print("ERROR: pose_landmarker.task is EMPTY!")
    print()
    print("The file size is 0 bytes.")
    print("You need to download the actual MediaPipe Pose Landmarker model.")
    print("=" * 60)

    exit()

# STEP 2: CREATE MEDIAPIPE POSE LANDMARKER
print()
print("Loading MediaPipe Pose Landmarker...")

# Create base options
base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)

# Create Pose Landmarker options
options = vision.PoseLandmarkerOptions(
    base_options=base_options,

    # Detect only one person
    num_poses=1,

    # Minimum confidence for detecting a person
    min_pose_detection_confidence=0.5,

    # Minimum confidence for pose tracking
    min_tracking_confidence=0.5
)

# Create Pose Landmarker
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
    print()
    print("Model path:")
    print(MODEL_PATH)
    print()
    print("Model size:")
    print(model_size, "bytes")
    print("=" * 60)

    exit()

print("MediaPipe Pose Landmarker initialized successfully!")

# STEP 3: OPEN OPENCV WEBCAM
print()
print("Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    detector.close()
    exit()

print("Webcam started successfully.")
print()
print("Stand in front of the camera.")
print("Your body will be detected using MediaPipe Pose.")
print()
print("Press Q to exit.")
print("=" * 60)

# STEP 4: LIVE CAMERA LOOP
while True:
    # Read frame from webcam
    success, frame = cap.read()
    if not success:
        print("ERROR: Failed to read camera frame.")
        break
    # Flip frame horizontally
    frame = cv2.flip(
        frame,
        1
    )
    
    # Get frame dimensions
    height, width, _ = frame.shape
   
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )
    # Convert OpenCV frame to MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )
    # STEP 5: DETECT BODY / POSE
    detection_result = detector.detect(
        mp_image
    )
   
    # STEP 6: CHECK IF A PERSON IS DETECTED
    if detection_result.pose_landmarks:
        # We only detect one person
        pose_landmarks = detection_result.pose_landmarks[0]
        
        # STEP 7: GET IMPORTANT BODY LANDMARKS
        # Left shoulder
        left_shoulder = pose_landmarks[11]

        # Right shoulder
        right_shoulder = pose_landmarks[12]

        # Left hip
        left_hip = pose_landmarks[23]

        # Right hip
        right_hip = pose_landmarks[24]

      
        # STEP 8: CALCULATE BODY CENTER
        # We calculate the center between
        # left and right shoulders
        center_x_normalized = (
            left_shoulder.x +
            right_shoulder.x
        ) / 2
        center_y_normalized = (
            left_shoulder.y +
            right_shoulder.y
        ) / 2
        # Convert normalized coordinates
        # to pixel coordinates

        center_x = int(
            center_x_normalized * width
        )

        center_y = int(
            center_y_normalized * height
        )

        # STEP 9: DRAW BODY CENTER
       
        cv2.circle(
            frame,
            (center_x, center_y),
            15,
            (0, 255, 255),
            -1
        )

        # STEP 10: DRAW BODY LANDMARKS
        for landmark in pose_landmarks:

            # Convert normalized coordinates
            # to pixel coordinates

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )

            # Draw landmark point
            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )
        
        # STEP 11: DRAW BODY CONNECTIONS
       
        for connection in (
            vision.PoseLandmarksConnections.POSE_LANDMARKS
        ):
            start = pose_landmarks[
                connection.start
            ]

            end = pose_landmarks[
                connection.end
            ]

            # Convert start point
            start_x = int(
                start.x * width
            )

            start_y = int(
                start.y * height
            )


            # Convert end point
            end_x = int(
                end.x * width
            )

            end_y = int(
                end.y * height
            )

            # Draw connection
            cv2.line(
                frame,
                (start_x, start_y),
                (end_x, end_y),
                (255, 0, 0),
                2
            )
        
        # STEP 12: DISPLAY BODY POSITION
        cv2.putText(
            frame,
            f"Body X: {center_x}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )
        cv2.putText(
            frame,
            f"Body Y: {center_y}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )
       
        # STEP 13: DETERMINE BODY DIRECTION
        # Define center region
        left_boundary = int(
            width * 0.35
        )

        right_boundary = int(
            width * 0.65
        )

       # Draw boundary lines
        cv2.line(
            frame,
            (left_boundary, 0),
            (left_boundary, height),
            (0, 0, 255),
            2
        )
        cv2.line(
            frame,
            (right_boundary, 0),
            (right_boundary, height),
            (0, 0, 255),
            2
        )

        # Determine body position
        if center_x < left_boundary:
            direction = "MOVE LEFT"

        elif center_x > right_boundary:
            direction = "MOVE RIGHT"

        else:
            direction = "CENTER / STOP"

        # Display direction
        cv2.putText(
            frame,
            direction,
            (width // 2 - 150, height - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            3
        )

    # STEP 14: NO PERSON DETECTED
    else:
       cv2.putText(
            frame,
            "NO BODY DETECTED",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    # STEP 15: SHOW LIVE CAMERA FEED
    cv2.imshow(
        "MediaPipe Body Follower",
        frame
    )
    # STEP 16: EXIT WITH Q
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print()
        print("Q pressed.")
        print("Closing camera...")

        break

# STEP 17: CLEANUP
cap.release()
cv2.destroyAllWindows()
detector.close()

print()
print("=" * 60)
print("MediaPipe Body Follower stopped.")
print("Camera closed.")
print("=" * 60)
