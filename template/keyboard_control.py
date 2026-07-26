import time
from pynput import keyboard
from pysimverse import Drone


# ============================================================
# DRONE SETUP
# ============================================================

drone = Drone()

print("Connecting to drone...")
drone.connect()

time.sleep(1)

print("Taking off...")
drone.take_off()

time.sleep(1)


# ============================================================
# CONTROL SETTINGS
# ============================================================

SPEED = 50
ROTATION_SPEED = 5

wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaawwwwwwwwwwwwwwwww
# ============================================================
# RC CONTROL VARIABLES
# ============================================================

left_right = 0
forward_backward = 0
up_down = 0
yaw = 0


# Used to safely stop the main control loop
running = True


# ============================================================
# KEY PRESS FUNCTION
# ============================================================

def on_press(key):
    global left_right
    global forward_backward
    global up_down
    global yaw
    global running

    try:

        # ---------------- Forward / Backward ----------------

        if key.char == "w":
            forward_backward = SPEED

        elif key.char == "s":
            forward_backward = -SPEED


        # ---------------- Left / Right ----------------

        elif key.char == "a":
            left_right = -SPEED

        elif key.char == "d":
            left_right = SPEED


        # ---------------- Rotation ----------------

        elif key.char == "q":
            yaw = -ROTATION_SPEED

        elif key.char == "e":
            yaw = ROTATION_SPEED


    except AttributeError:

        # ---------------- Arrow Keys ----------------

        if key == keyboard.Key.up:
            up_down = SPEED

        elif key == keyboard.Key.down:
            up_down = -SPEED


        # ---------------- Emergency Stop ----------------

        elif key == keyboard.Key.space:
            left_right = 0
            forward_backward = 0
            up_down = 0
            yaw = 0

            print("STOP")


        # ---------------- Land and Exit ----------------

        elif key == keyboard.Key.esc:
            print("ESC pressed.")
            print("Landing drone...")

            running = False

            # Stop all movement first
            left_right = 0
            forward_backward = 0
            up_down = 0
            yaw = 0


# ============================================================
# KEY RELEASE FUNCTION
# ============================================================

def on_release(key):
    global left_right
    global forward_backward
    global up_down
    global yaw

    try:

        # ---------------- Forward / Backward ----------------

        if key.char == "w" or key.char == "s":
            forward_backward = 0


        # ---------------- Left / Right ----------------

        elif key.char == "a" or key.char == "d":
            left_right = 0


        # ---------------- Rotation ----------------

        elif key.char == "q" or key.char == "e":
            yaw = 0


    except AttributeError:

        # ---------------- Arrow Keys ----------------

        if key == keyboard.Key.up or key == keyboard.Key.down:
            up_down = 0


# ============================================================
# START KEYBOARD LISTENER
# ============================================================

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

listener.start()


# ============================================================
# DISPLAY CONTROLS
# ============================================================

print()
print("==========================================")
print("       PYSIMVERSE KEYBOARD CONTROL")
print("==========================================")
print()
print("W / S       : Forward / Backward")
print("A / D       : Left / Right")
print("UP / DOWN   : Up / Down")
print("Q / E       : Rotate Left / Right")
print("SPACE       : Emergency Stop")
print("ESC         : Land and Exit")
print()
print("Hold a key to move.")
print("Release the key to stop that movement.")
print("==========================================")
print()


# ============================================================
# MAIN RC CONTROL LOOP
# ============================================================

try:

    while running:

        # Send current RC control values
        drone.send_rc_control(
            left_right,
            forward_backward,
            up_down,
            yaw
        )

        # Control loop rate
        time.sleep(0.05)


# ============================================================
# SAFETY HANDLING
# ============================================================

except KeyboardInterrupt:

    print()
    print("Program interrupted.")
    print("Landing drone...")


finally:

    # Stop movement before landing
    drone.send_rc_control(
        0,
        0,
        0,
        0
    )

    time.sleep(0.5)

    # Land drone
    drone.land()

    time.sleep(1)

    # Stop keyboard listener
    listener.stop()

    print("Drone landed.")
    print("Program ended.")
