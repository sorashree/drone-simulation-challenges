# 🚁 Drone Simulation Challenges

A robotics and computer vision project focused on controlling and programming a simulated drone using Python.

This repository contains my completed drone simulation challenges, covering fundamental drone control, computer vision, hand tracking, color detection, and vision-based navigation.

The project was developed as a hands-on learning experience to strengthen my understanding of **robotics, Python programming, computer vision, control systems, and embedded-oriented thinking**.

---

## 🎯 Project Overview

The goal of this project was to solve a series of drone control and computer vision challenges in a simulated environment.

Throughout the project, I worked on concepts including:

* Drone takeoff and landing
* Real-time drone control
* Remote control (RC) commands
* Webcam-based computer vision
* Hand landmark detection
* Gesture-based drone control
* Color detection using HSV
* Image masking
* Centroid detection
* Line tracking
* PD (Proportional-Derivative) control
* Lateral movement control
* Yaw / heading control
* Dynamic forward-speed control
* Real-time visual feedback
* Safe drone shutdown and landing

The project helped me understand how **perception, decision-making, and control** can be combined to create intelligent robotic systems.

---

## 🧠 System Architecture

The core idea behind the computer-vision-based challenges can be represented as:

```text
                Camera / Video Feed
                        │
                        ▼
                Computer Vision
                        │
                        ▼
              Feature / Object Detection
                        │
                        ▼
                 Position Analysis
                        │
                        ▼
                   Error Calculation
                        │
                        ▼
                 Control Algorithm
                        │
                        ▼
                  Drone Commands
                        │
                        ▼
                    Drone Motion
                        │
                        └───────────────┐
                                        │
                         Continuous Feedback Loop
                                        │
                                        └──────────►
```

This follows a fundamental robotics pipeline:

> **Perception → State Estimation → Decision → Control → Action**

---

## 🛠️ Technologies Used

* **Python**
* **OpenCV**
* **NumPy**
* **MediaPipe**
* **CVZone**
* **PySimverse**
* **HSV Color Space**
* **PD Control**
* **Computer Vision**
* **Drone Simulation**

---

## 📂 Project Structure

```text
drone-simulation-challenges/
│
├── Mission 1/
│   └── ...
│
├── Mission 2/
│   └── ...
│
├── Mission 3/
│   └── ...
│
├── Mission 4/
│   └── ...
│
├── Mission 5/
│   └── ...
│
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

> The exact folder structure may vary depending on the organization of individual challenges.

---

# 🚀 Challenges Completed

## Mission 1 — Basic Drone Control

Implemented fundamental drone operations and control commands.

### Concepts Covered

* Drone connection
* Takeoff
* Landing
* RC control
* Directional movement
* Keyboard-based control

---

## Mission 2 — Drone Movement and Control

Worked with drone movement commands and control logic.

### Concepts Covered

* Forward and backward movement
* Left and right movement
* Vertical movement
* Yaw control
* Real-time user input

---

## Mission 3 — Color Detection

Implemented color-based object detection using the HSV color space.

The system converts the camera image from BGR to HSV and creates a binary mask based on selected color ranges.

### Processing Pipeline

```text
Camera Frame
     │
     ▼
BGR → HSV Conversion
     │
     ▼
Color Range Filtering
     │
     ▼
Binary Mask
     │
     ▼
Detected Color Region
```

The implementation also supports HSV tuning using OpenCV trackbars.

---

## Mission 4 — Hand Position Detection & Drone Control

Used **MediaPipe Hand Landmarker** and **OpenCV** to control the drone based on the horizontal position of a detected hand.

### Control Logic

```text
Hand on LEFT   → Drone moves LEFT

Hand in CENTER → Drone STOPS

Hand on RIGHT  → Drone moves RIGHT

No Hand       → Drone STOPS
```

The camera frame is divided into three regions:

```text
┌──────────────┬────────────────┬──────────────┐
│     LEFT     │    DEADZONE    │    RIGHT     │
│              │                │              │
│   Move Left  │     STOP       │  Move Right  │
└──────────────┴────────────────┴──────────────┘
```

The wrist landmark is used as the reference point to determine the hand's horizontal position.

### Technologies

* OpenCV
* MediaPipe
* Hand Landmarks
* Real-time Computer Vision
* Drone Control

---

## Mission 5 — Vision-Based Line Tracking & Drone Control

Implemented a vision-based drone controller that detects a colored line and uses its position to control the drone.

The system divides the detected line into two regions:

* **Bottom region** — used for lateral alignment
* **Top region** — used to anticipate heading and turns

The centroid of each region is calculated using image moments.

### Control System

```text
                 Camera
                    │
                    ▼
              Detect Colored Line
                    │
                    ▼
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
    Bottom Centroid      Top Centroid
          │                   │
          ▼                   ▼
    Lateral Error        Heading Error
          │                   │
          ▼                   ▼
    L/R Controller        Yaw Controller
          │                   │
          └─────────┬─────────┘
                    ▼
              Forward Control
                    │
                    ▼
              Drone Movement
```

### PD Control

The drone uses a PD-based control approach:

```text
Control Output = Kp × Error + Kd × Change in Error
```

This allows the drone to react to the position of the detected line while reducing sudden oscillations.

The controller dynamically adjusts forward speed depending on the detected lateral and heading errors.

When the line is lost, the drone stops its movement and enters a safe hovering state until the line is detected again.

---

# 🎥 Project Demonstrations

Below are selected demonstrations of the completed challenges.

### 🎬 Demonstration 1

https://youtu.be/HePDO0JEnh0?si=WQ7WkmrrGEk9Cp4F

> Brief description: Demonstration of [Mission 4] showing the drone responding to real-time computer vision input.

### 🎬 Demonstration 2

https://youtu.be/ReEW46AyqsY?si=IwFj9AEdOM0z2n_-

> Brief description: Demonstration of [Mission 5] showing vision-based drone control and navigation.

---

## 📸 Visual Results

Screenshots and additional demonstrations can be added here to showcase:

* Hand tracking
* Color detection
* Line detection
* PD control visualization
* Drone movement
* Real-time telemetry

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/sorashree/drone-simulation-challenges.git
```

```bash
cd drone-simulation-challenges
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run a Challenge

Navigate to the required mission directory and run the corresponding Python script.

For example:

```bash
python mission3.py
```

> The exact command depends on the file and folder structure of each mission.

---

# 🎮 Controls

Depending on the challenge, control methods include:

* Keyboard input
* Hand position
* Computer vision
* Color-based tracking
* Autonomous control logic

For hand-controlled missions:

```text
LEFT REGION    → Move Drone Left
CENTER REGION  → Stop
RIGHT REGION   → Move Drone Right
NO HAND        → Stop
Q              → Exit
```

---

# 📚 Key Learnings

Through this project, I gained practical experience in:

### Robotics

* Understanding drone movement and control
* Working with real-time control loops
* Designing perception-to-action pipelines

### Computer Vision

* Image acquisition
* Color space conversion
* HSV-based segmentation
* Binary masks
* Hand landmark detection
* Centroid calculation
* Image moments

### Control Systems

* Error calculation
* Proportional control
* Derivative control
* PD controllers
* Dynamic speed adjustment
* Feedback-based control

### Python Development

* Object-oriented programming
* Classes and methods
* Exception handling
* Real-time processing loops
* Modular code organization

---

# 🔮 Future Improvements

Possible future improvements include:

* Implementing more robust line detection
* Improving controller tuning for higher-speed navigation
* Adding PID control
* Implementing obstacle avoidance
* Adding object detection
* Integrating ROS 2
* Connecting vision-based perception with robotic navigation
* Testing the algorithms on a physical drone or robot

---

# 🧑‍💻 Author

**Shreeya Mukherjee**

Engineering Student | Robotics & Embedded Systems Enthusiast

Interested in:

* Robotics
* Embedded Systems
* Computer Vision
* ROS 2
* Autonomous Systems
* AI & Robotics

---


⭐ If you find this project useful or interesting, feel free to explore the code and learn from the implementations.
