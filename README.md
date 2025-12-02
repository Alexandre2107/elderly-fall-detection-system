# Elderly Fall Detection System

<div align="center">

![GitHub last commit](https://img.shields.io/github/last-commit/Alexandre2107/elderly-fall-detection-system?style=for-the-badge)
![Top Language](https://img.shields.io/github/languages/top/Alexandre2107/elderly-fall-detection-system?style=for-the-badge)
![Languages Count](https://img.shields.io/github/languages/count/Alexandre2107/elderly-fall-detection-system?style=for-the-badge)
![Repository Size](https://img.shields.io/github/repo-size/Alexandre2107/elderly-fall-detection-system?style=for-the-badge)

</div>

---

## Tools & Technologies

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logo=google&logoColor=white)
![Markdown](https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Getting Started](#-getting-started)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Testing](#-testing)

---

## Overview

The **Elderly Fall Detection System** is an intelligent real-time monitoring solution designed to detect falls in elderly individuals using computer vision and pose estimation technology. The system leverages **MediaPipe** for human pose detection and **Flask** for web-based video streaming, providing an accessible interface for monitoring.

### Key Features

- **Real-time Fall Detection**: Uses MediaPipe Pose to analyze body movements and detect falls
- **Automated Alerts**: Sends SMS notifications and makes emergency calls via GSM SIM800L module
- **Web Interface**: Flask-based web application for live video monitoring
- **Multi-stage Detection**: Implements velocity tracking, torso angle analysis, and aspect ratio calculations
- **Configurable Thresholds**: Adjustable parameters for detection sensitivity
- **Performance Monitoring**: Built-in system metrics tracking (CPU and RAM usage)

---

## Getting Started

This project was developed and tested using the following hardware components:

### Hardware Components

- **Webcam**: For real-time video capture and monitoring
- **Raspberry Pi 4 Model B**: Main processing unit running the fall detection system
- **GSM SIM800L Module**: For sending SMS alerts and making emergency calls

### System Architecture

The system captures video frames from the webcam, processes them using MediaPipe for pose estimation, analyzes body position and movement patterns, and triggers alerts through the GSM module when a fall is detected.

---

## Prerequisites

Before installing the system, ensure you have the following:

### Hardware Requirements

- Raspberry Pi 4 Model B (or compatible system)
- USB Webcam or Raspberry Pi Camera Module
- GSM SIM800L Module with active SIM card
- Stable power supply for Raspberry Pi and GSM module

### Software Requirements

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### System Permissions

- Access to serial ports (for GSM module communication)
- Camera permissions

---

## Installation

Follow these steps to set up the Elderly Fall Detection System:

### 1. Clone the Repository

```bash
git clone https://github.com/Alexandre2107/elderly-fall-detection-system.git
cd elderly-fall-detection-system
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Hardware

#### GSM Module Setup

1. Connect the GSM SIM800L module to the Raspberry Pi's serial port
2. Default serial port: `/dev/serial0` (configurable in `app.py`)
3. Ensure the SIM card is inserted and has credit for SMS/calls

#### Camera Setup

The system automatically detects available cameras. If you need to specify a camera index, modify the `find_camera_index()` function in `app.py`.

### 5. Configure Alert Settings

Edit `app.py` to set your emergency contact number:

```python
numero_alerta = "+5535999092107"  # Replace with your number
```

---

## Usage

### Starting the Application

Run the Flask application:

```bash
python app.py
```

The web interface will be accessible at:
- Local: `http://localhost:5000`
- Network: `http://<raspberry-pi-ip>:5000`

### Accessing the Web Interface

1. Open a web browser
2. Navigate to `http://<raspberry-pi-ip>:5000`
3. The live video feed with fall detection overlay will be displayed

### System States

The system operates in four states:

- **Estavel** (Stable): Person is standing upright
- **Caindo** (Falling): High velocity downward movement detected
- **Instavel** (Unstable): Person is in a non-upright position
- **Queda Confirmada** (Fall Confirmed): Fall confirmed after threshold time (4.5 seconds)

### Alert Mechanism

When a fall is confirmed:
1. SMS alert is sent to the configured number
2. Automated call is initiated with rapid tone alerts
3. System continues monitoring

---

## Testing

The project includes comprehensive testing suites for validation:

### Fall Detection Tests

Located in `data_set_codes/`:

```bash
# Quick fall detection test
python data_set_codes/teste_rapido.py

# Automated fall detection test with dataset
python data_set_codes/automated_fall_detection_test.py

# Analyze fall detection results
python data_set_codes/analisar_resultados.py
```

### ADL (Activities of Daily Living) Tests

Located in `data_set_ADL_codes/`:

```bash
# Quick ADL test
python data_set_ADL_codes/teste_rapido_adl.py

# Automated ADL test
python data_set_ADL_codes/adl_test_automated.py

# Controlled environment analysis
python data_set_ADL_codes/analise_ambiente_controlado.py

# Complete precision analysis
python data_set_ADL_codes/analise_completa_precisao.py
```

### GSM Module Tests

```bash
# Test GSM module functionality
python test_gsm.py

# Test GSM SOS alerts
python test_gsm_sos.py
```

### Audio Tests

```bash
# Test audio functionality
python test_audio.py

# Upload audio samples
python upload_audio.py
```

### Test Datasets

- **Fall Detection Videos**: `data_set_codes/data_set_videos/`
- **ADL Videos**: `data_set_ADL_codes/data_set_videos_ADL/`

---

## Performance Metrics

The system tracks and logs:
- Fall detection latency
- SMS alert latency
- CPU usage
- RAM consumption
- Confirmation time

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is available for educational and research purposes.

---

## Author

**Alexandre Rodrigues**

---

## Contact

For emergency alerts, configure your contact number in the `app.py` file.

---

<div align="center">

**Made with ❤️ for elderly safety**

</div>