import cv2
import mediapipe as mp

from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# STEP 1: FIND THE MEDIAPIPE HAND LANDMARKER MODEL
# ============================================================

# __file__ is:
# Pysimverse_drone/template/hand_gesture_mediapipe.py
#
# .parent       -> template
# .parent.parent -> Pysimverse_drone

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "hand_landmarker.task"


print("=" * 60)
print("MEDIAPIPE HAND LANDMARKER")
print("=" * 60)

print("Looking for model at:")
print(MODEL_PATH)


# ============================================================
# CHECK IF MODEL EXISTS
# ============================================================

if not MODEL_PATH.exists():

    print()
    print("ERROR: hand_landmarker.task was not found!")
    print()
    print("Please put the real MediaPipe model file here:")
    print(MODEL_PATH)
    print()
    print("Do not create an empty file manually.")
    print("=" * 60)

    exit()


# ============================================================
# CHECK MODEL FILE SIZE
# ============================================================

model_size = MODEL_PATH.stat().st_size

print("Model found!")
print("Model size:", model_size, "bytes")


# Check if the file is empty
if model_size == 0:

    print()
    print("ERROR: hand_landmarker.task is EMPTY!")
    print()
    print("The file size is 0 bytes.")
    print("You need to download the actual MediaPipe Hand Landmarker model.")
    print("=" * 60)

    exit()


# ============================================================
# STEP 2: CREATE MEDIAPIPE HAND LANDMARKER
# ============================================================

print()
print("Loading MediaPipe Hand Landmarker...")


# Create base options
base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)


# Create Hand Landmarker options
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2
)


# Create Hand Landmarker
try:

    detector = vision.HandLandmarker.create_from_options(
        options
    )

except Exception as error:

    print()
    print("ERROR: Could not initialize MediaPipe Hand Landmarker.")
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


print("MediaPipe Hand Landmarker initialized successfully!")


# ============================================================
# STEP 3: OPEN OPENCV WEBCAM
# ============================================================

print()
print("Opening webcam...")


cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Could not open webcam.")

    detector.close()

    exit()


print("Webcam started successfully.")
print()
print("Show your hand to the camera.")
print("You can show up to 2 hands.")
print()
print("Press Q to exit.")
print("=" * 60)


# ============================================================
# STEP 4: LIVE CAMERA LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # Read frame from webcam
    # --------------------------------------------------------

    success, frame = cap.read()


    if not success:

        print("ERROR: Failed to read camera frame.")

        break


    # --------------------------------------------------------
    # Flip frame horizontally
    # --------------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )


    # --------------------------------------------------------
    # Convert BGR to RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # Convert OpenCV frame to MediaPipe Image
    # --------------------------------------------------------

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # ========================================================
    # STEP 5: DETECT HANDS
    # ========================================================

    detection_result = detector.detect(
        mp_image
    )


    # ========================================================
    # STEP 6: DRAW HAND LANDMARKS
    # ========================================================

    if detection_result.hand_landmarks:

        # Loop through every detected hand
        for hand_index, hand_landmarks in enumerate(
            detection_result.hand_landmarks
        ):

            # ------------------------------------------------
            # Draw all 21 landmarks
            # ------------------------------------------------

            for landmark in hand_landmarks:

                # Convert normalized coordinates
                # to pixel coordinates

                x = int(
                    landmark.x * frame.shape[1]
                )

                y = int(
                    landmark.y * frame.shape[0]
                )


                # Draw landmark point
                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )


            # ------------------------------------------------
            # Draw connections between landmarks
            # ------------------------------------------------

            for connection in (
                vision.HandLandmarksConnections.HAND_CONNECTIONS
            ):

                start = hand_landmarks[
                    connection.start
                ]

                end = hand_landmarks[
                    connection.end
                ]


                # Convert start point
                start_x = int(
                    start.x * frame.shape[1]
                )

                start_y = int(
                    start.y * frame.shape[0]
                )


                # Convert end point
                end_x = int(
                    end.x * frame.shape[1]
                )

                end_y = int(
                    end.y * frame.shape[0]
                )


                # Draw connection line
                cv2.line(
                    frame,
                    (start_x, start_y),
                    (end_x, end_y),
                    (255, 0, 0),
                    2
                )


            # ------------------------------------------------
            # Display hand number
            # ------------------------------------------------

            wrist = hand_landmarks[0]


            wrist_x = int(
                wrist.x * frame.shape[1]
            )

            wrist_y = int(
                wrist.y * frame.shape[0]
            )


            cv2.putText(
                frame,
                f"Hand {hand_index + 1}",
                (wrist_x, wrist_y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )


    # ========================================================
    # STEP 7: DISPLAY NUMBER OF DETECTED HANDS
    # ========================================================

    if detection_result.hand_landmarks:

        number_of_hands = len(
            detection_result.hand_landmarks
        )

    else:

        number_of_hands = 0


    cv2.putText(
        frame,
        f"Hands detected: {number_of_hands}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


    # ========================================================
    # STEP 8: SHOW LIVE CAMERA FEED
    # ========================================================

    cv2.imshow(
        "PySimVerse - MediaPipe Hand Detection",
        frame
    )


    # ========================================================
    # STEP 9: EXIT WITH Q
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        print()
        print("Q pressed.")
        print("Closing camera...")

        break


# ============================================================
# STEP 10: CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

detector.close()


print()
print("=" * 60)
print("MediaPipe Hand Detection stopped.")
print("Camera closed.")
print("=" * 60)
