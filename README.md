# 🚁 Drone Simulation Challenges

A Python-based robotics and computer vision project focused on developing and controlling a simulated drone using **PySimverse**.

The project explores the integration of **computer vision, real-time perception, and drone control** through a series of progressively challenging missions.

## 🚀 Key Features

* Basic drone flight and RC control
* Keyboard-based drone movement
* HSV-based color detection
* MediaPipe hand tracking and gesture-based control
* Vision-based line tracking
* PD-based control for navigation
* Real-time body tracking for drone movement
* Safe drone stop and landing logic

## 🧠 Mission Overview

### Mission 1–2 — Drone Control

Implemented fundamental drone operations including connection, takeoff, landing, directional movement, and RC control.

### Mission 3 — Color Detection

Built a real-time color detection pipeline using **OpenCV and HSV segmentation** for identifying and tracking colored regions.

### Mission 4 — Hand Tracking Control

Used **MediaPipe Hand Landmarker** to control the drone based on the detected hand position.

**Hand Left → Drone Left | Center → Stop | Hand Right → Drone Right**

### Mission 5 — Vision-Based Line Tracking

Developed a computer-vision-based navigation system that detects a colored line and uses centroid analysis with **PD control** to regulate lateral movement, heading, and forward speed.

### Mission 6 — Body Follower

Implemented real-time human body tracking using **MediaPipe Pose Landmarker**. The system maps the user's body position to drone movement commands.

**Body Left → Drone Left**
**Body Right → Drone Right**
**Body Up → Drone Up**
**Body Down → Drone Down**
**Body Center → Stable Position**

This mission demonstrates a complete **Perception → Decision → Control** pipeline.

## 🛠️ Technologies

* Python
* OpenCV
* MediaPipe
* NumPy
* CVZone
* PySimverse
* Computer Vision
* PD Control
* Real-Time Robotics Control

## 📂 Project Structure

```text
drone-simulation-challenges/
│
├── mission3_*.py
├── mission4_*.py
├── mission5_*.py
├── mission6_body_follower.py
├── pose_landmarker.task
├── template/
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation

```bash
git clone https://github.com/sorashree/drone-simulation-challenges.git
cd drone-simulation-challenges
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run Mission 6:

```bash
python mission6_body_follower.py
```

> Requires a working webcam and the MediaPipe `pose_landmarker.task` model file.

## 🎥 Demonstrations

* [Mission 4 — Hand Tracking Drone Control]
* (https://youtu.be/HePDO0JEnh0)
* [Mission 5 — Vision-Based Line Tracking]
* (https://youtu.be/ReEW46AyqsY)
* [Mission 6- Body Follower Drone]
* (https://youtube.com/shorts/buv27pSFhDQ?si=I8b66jVCzSRW2rQI)

## 📚 Key Skills Demonstrated

**Robotics:** Drone control, feedback loops, perception-to-action systems

**Computer Vision:** OpenCV, MediaPipe, HSV segmentation, landmark detection, centroid tracking

**Control Systems:** Error calculation, proportional-derivative control, dynamic movement control

**Software Development:** Python, real-time processing, modular code, exception handling, safe shutdown

## 🔮 Future Work

* ROS 2 integration
* Obstacle avoidance
* Object detection and tracking
* PID-based control
* Autonomous navigation
* Deployment on physical robotic platforms

## 👩‍💻 Author

**Shreeya Mukherjee**
Engineering Student | Robotics & Embedded Systems Enthusiast

**Interests:** Robotics · Embedded Systems · Computer Vision · ROS 2 · Autonomous Systems · AI & Robotics
