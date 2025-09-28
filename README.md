# Fall Detection System using MediaPipe

This project is a real-time monitoring system, developed as a Final Course Project (TCC), that uses computer vision to detect human falls, with a special focus on the safety of the elderly.

The web application, built with the Flask micro-framework, processes a live video stream from a camera. Body pose detection is performed by the **MediaPipe Pose** solution, which estimates the location of 33 key body landmarks. The system's logic analyzes vertical velocity, torso orientation, and body aspect ratio to identify patterns consistent with a fall.

Upon confirming a fall, the system automatically triggers a GSM module to send an **SMS alert** and place an **emergency call** to a pre-configured number, ensuring a rapid response.

---

## Technologies Used
* **Python 3.11**
* **Flask:** A web framework for serving the application and video stream.
* **OpenCV:** A computer vision library for video capture and manipulation.
* **MediaPipe:** Google's solution for detecting body pose landmarks.
* **PySerial:** A library for communicating with the serial port (GSM module).
* **Psutil:** A library for monitoring system resources (CPU and RAM).

---

## Setup and Usage

Follow the steps below to set up and run the project in your local environment.

**1. Clone the repository:**
```bash
git clone [https://github.com/Alexandre2107/elderly-fall-detection-system.git](https://github.com/Alexandre2107/elderly-fall-detection-system.git)
cd elderly-fall-detection-system
```

**2. Create and activate a virtual environment:**
```bash
# For Linux / macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

**3. Install the dependencies:**
Ensure the virtual environment is activated and install all the necessary libraries.
```bash
pip install -r requirements.txt
```
**Note:** You may need to configure permissions for the `/dev/serial0` serial port on the Raspberry Pi.

**4. Run the application:**
```bash
python app.py
```

**5. Access in your browser:**
Open your browser and navigate to your Raspberry Pi's IP address on the network (e.g., `http://192.168.1.10:5000`) to see the system in action.

---

## How It Works

1.  **Video Capture:** OpenCV captures the feed from the camera.
2.  **Pose Detection:** MediaPipe processes each frame, identifying 33 key body landmarks.
3.  **Fall Analysis:** A custom algorithm analyzes the following factors:
    * **High Vertical Velocity:** A rapid downward movement of the hip.
    * **Horizontal Position:** The body remains in a non-upright position after the rapid movement.
    * **Confirmation Time:** The system waits for a few seconds in the "unstable" state to prevent false positives.
4.  **Emergency Alert:** If the fall criteria are met, `pyserial` sends AT commands to the GSM module, which triggers the SMS and call.
