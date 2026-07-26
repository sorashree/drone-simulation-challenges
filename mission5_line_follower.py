from cvzone.ColorModule import ColorFinder
"""
Color Module
Finds color in an image based on hsv values
Can run as stand alone to find relevant hsv values

"""

import cv2
import numpy as np
import time
# pyrefly: ignore [missing-import]
from pysimverse import Drone

import cvzone


class ColorFinder:
    def __init__(self, trackBar=True):
        """
        :param trackBar: Whether to use OpenCV trackbars to dynamically adjust HSV values. Default is False.
        """
        self.trackBar = trackBar
        if self.trackBar:
            self.initTrackbars()

    def empty(self, a):
        """An empty function to pass as a parameter when creating trackbars."""
        pass

    def initTrackbars(self):
        """Initialize the OpenCV trackbars for dynamic HSV value adjustment."""
        cv2.namedWindow("TrackBars")
        cv2.resizeWindow("TrackBars", 640, 240)
        cv2.createTrackbar("Hue Min", "TrackBars", 0, 179, self.empty)
        cv2.createTrackbar("Hue Max", "TrackBars", 179, 179, self.empty)
        cv2.createTrackbar("Sat Min", "TrackBars", 0, 255, self.empty)
        cv2.createTrackbar("Sat Max", "TrackBars", 255, 255, self.empty)
        cv2.createTrackbar("Val Min", "TrackBars", 0, 255, self.empty)
        cv2.createTrackbar("Val Max", "TrackBars", 255, 255, self.empty)

    def getTrackbarValues(self):
        """
         Get the current HSV values set by the trackbars.

         :return: A dictionary containing the current HSV values from the trackbars.
         """
        hmin = cv2.getTrackbarPos("Hue Min", "TrackBars")
        smin = cv2.getTrackbarPos("Sat Min", "TrackBars")
        vmin = cv2.getTrackbarPos("Val Min", "TrackBars")
        hmax = cv2.getTrackbarPos("Hue Max", "TrackBars")
        smax = cv2.getTrackbarPos("Sat Max", "TrackBars")
        vmax = cv2.getTrackbarPos("Val Max", "TrackBars")

        hsvVals = {"hmin": hmin, "smin": smin, "vmin": vmin,
                   "hmax": hmax, "smax": smax, "vmax": vmax}
        print(hsvVals)
        return hsvVals

    def update(self, img, myColor=None):
        """
        Find a specified color in the given image.

        :param img: The image in which to find the color.
        :param myColor: The color to find, can be a string or None.

        :return: A tuple containing a mask image with only the specified color, and the original image masked to only show the specified color.
        """
        imgColor = []
        mask = []

        if self.trackBar:
            myColor = self.getTrackbarValues()

        if isinstance(myColor, str):
            myColor = self.getColorHSV(myColor)

        if myColor is not None:
            imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower = np.array([myColor['hmin'], myColor['smin'], myColor['vmin']])
            upper = np.array([myColor['hmax'], myColor['smax'], myColor['vmax']])
            mask = cv2.inRange(imgHSV, lower, upper)
            imgColor = cv2.bitwise_and(img, img, mask=mask)

        return imgColor, mask


if __name__ == "__main__":
    # Create an instance of the ColorFinder class with trackBar.
    # Set trackBar to False to run automatically without popups. Change to True if HSV tuning is needed.
    myColorFinder = ColorFinder(trackBar=False)

    # Initialize the drone camera feed.
    drone = Drone()
    drone.connect()
    time.sleep(1)
    drone.streamon()
    drone.take_off(takeoff_height=30)

    # Custom color values for detecting red.
    # Since red spans both ends of the HSV spectrum, we define dual ranges:
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    # PD controller coefficients
    # Lateral (left-right) PD coefficients
    Kp_lat = 0.10
    Kd_lat = 0.025
    prev_lat_error = 0

    # Heading (yaw) PD coefficients
    Kp_yaw = 0.10
    Kd_yaw = 0.025
    prev_head_error = 0

    try:
        # Main loop to continuously get frames from the drone camera.
        while True:
            # Read the current frame from the drone camera.
            img, is_success = drone.get_frame()
            if not is_success:
                continue

            # Convert to HSV and create a combined mask for red
            imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask1 = cv2.inRange(imgHSV, lower_red1, upper_red1)
            mask2 = cv2.inRange(imgHSV, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
            imgRed = cv2.bitwise_and(img, img, mask=mask)

            # Get dimensions of frame
            h, w = img.shape[:2]
            cx_center = w // 2

            # Split mask into bottom and top region for multi-region centroid tracking
            # Bottom region tracking (closest to drone) for lateral alignment
            bottom_mask = mask[h//2:h, :]
            # Top region tracking (further ahead) for heading anticipation
            top_mask = mask[0:h//2, :]

            M_bottom = cv2.moments(bottom_mask)
            M_top = cv2.moments(top_mask)
            M_all = cv2.moments(mask)

            left_right = 0
            forward = 0
            yaw = 0
            lat_error = 0
            head_error = 0
            line_detected = False

            if M_all["m00"] > 150:
                line_detected = True

                # Compute bottom centroid (lateral offset point)
                if M_bottom["m00"] > 50:
                    cx_bottom = int(M_bottom["m10"] / M_bottom["m00"])
                else:
                    cx_bottom = int(M_all["m10"] / M_all["m00"])

                # Compute top centroid (look-ahead point)
                if M_top["m00"] > 50:
                    cx_top = int(M_top["m10"] / M_top["m00"])
                else:
                    cx_top = cx_bottom

                # Calculate errors
                lat_error = cx_bottom - cx_center
                head_error = cx_top - cx_bottom

                # PD Control for Lateral (left/right) movement
                d_lat = lat_error - prev_lat_error
                left_right = int(np.clip(Kp_lat * lat_error + Kd_lat * d_lat, -30, 30))
                prev_lat_error = lat_error

                # PD Control for Heading (yaw) movement
                d_head = head_error - prev_head_error
                yaw = int(np.clip(Kp_yaw * head_error + Kd_yaw * d_head, -25, 25))
                prev_head_error = head_error

                # Dynamic forward speed: go faster when straight/aligned, slow down on turns/errors
                forward = 20 - int(abs(lat_error) * 0.08) - int(abs(head_error) * 0.08)
                forward = int(np.clip(forward, 6, 20))

                # Draw tracking visualizations on the image
                # Red centerline of the screen
                cv2.line(img, (cx_center, 0), (cx_center, h), (0, 0, 255), 1)
                # Centroid of bottom region (green circle)
                cv2.circle(img, (cx_bottom, 3 * h // 4), 8, (0, 255, 0), -1)
                # Centroid of top region (yellow circle)
                cv2.circle(img, (cx_top, h // 4), 8, (0, 255, 255), -1)
                # Line showing heading direction (blue line)
                cv2.line(img, (cx_bottom, 3 * h // 4), (cx_top, h // 4), (255, 0, 0), 2)
            else:
                # Keep hovering and reset error states to prevent derivative spike on recovery
                left_right = 0
                forward = 0
                yaw = 0
                prev_lat_error = 0
                prev_head_error = 0
                cv2.putText(img, "LINE LOST - HOVERING", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Send the RC command to control the drone (left_right, forward_backward, up_down, yaw)
            drone.send_rc_control(left_right, forward, 0, yaw)

            # Add telemetry data onto the screen
            cv2.putText(img, f"Lat Error: {lat_error}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"Head Error: {head_error}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"L/R Control: {left_right}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"Yaw Control: {yaw}", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"Forward: {forward}", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Stack the original image (with overlays), the masked color image, and the binary mask.
            imgStack = cvzone.stackImages([img, imgRed, mask], 3, 1)

            # Show the stacked images.
            cv2.imshow("Image Stack", imgStack)

            # Break the loop if the 'q' key is pressed.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")

    finally:
        # Land the drone and clean up
        print("Landing drone...")
        drone.send_rc_control(0, 0, 0, 0)
        time.sleep(0.5)
        drone.land()
        time.sleep(1)
        cv2.destroyAllWindows()
        print("Program finished.")
