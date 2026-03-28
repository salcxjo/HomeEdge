# HomeEdge — Local Edge Intelligence for Home Monitoring

A distributed IoT system combining embedded sensing, computer vision, and on-device machine learning for home environmental monitoring and security — built entirely on local hardware with no cloud dependencies.

## Project Overview

HomeEdge is a multi-phase embedded systems and edge ML project that integrates:
- Wireless sensor nodes (Raspberry Pi Pico 2W) with environmental and motion sensing
- Computer vision pipeline (Raspberry Pi 4) with real-time person detection
- Custom-trained anomaly detection models running inference locally
- Live web dashboard for monitoring and control

**Status:** Phases 1–7 complete and deployed. Ongoing development focuses on expanded ML capabilities and multi-node scaling.

---

## System Architecture
```
[Pico 2W Node]                    [Raspberry Pi 4]
  ├─ DHT11 (temp/humidity)  ──→   ├─ Mosquitto MQTT Broker
  ├─ BMP180 (pressure)      MQTT  ├─ Pi Camera + OpenCV
  ├─ HC-SR501 (PIR motion)  ──→   ├─ TFLite Person Detection
  ├─ GL5516 (light level)         ├─ PyTorch Anomaly Detection
  ├─ SW-520D (tamper)             └─ Streamlit Dashboard
  ├─ SH1107 OLED display              ↓
  └─ Active buzzer alerts         SQLite (local storage)
```

---

## Technical Highlights

### Phase 1–2: Distributed Sensing & Communication
- MicroPython firmware on Pico 2W with multi-sensor integration (I2C, SPI, ADC, GPIO)
- MQTT pub/sub architecture for reliable wireless telemetry
- Local OLED feedback and physical controls (buttons, relay, buzzer)

### Phase 3–4: Computer Vision Pipeline
- OpenCV background subtraction (MOG2) for motion detection on Pi 4 CPU
- TensorFlow Lite MobileNet SSD for real-time person detection
- Confidence-thresholded inference with bounding box visualization

### Phase 5–6: Expanded Sensing
- Six concurrent data streams: temp, humidity, pressure, light, motion, tamper
- Analog sensor integration via Pico's ADC
- Physical LED status panel and potentiometer-based threshold controls

### Phase 7: Edge ML & Anomaly Detection
- Custom PyTorch autoencoder trained on local environmental data
- Real-time reconstruction error analysis for anomaly flagging
- Model quantization and deployment to edge hardware
- SQLite-backed event logging and dashboard integration

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Embedded | MicroPython, C/C++ (future Arduino expansion) |
| Networking | MQTT (Mosquitto), WiFi (802.11n) |
| Computer Vision | OpenCV, TensorFlow Lite |
| Machine Learning | PyTorch, scikit-learn, XGBoost (planned) |
| Data | SQLite, Pandas |
| Frontend | Streamlit, Plotly |
| Hardware | Raspberry Pi Pico 2W, Pi 4, DHT11, BMP180, HC-SR501, SH1107 OLED |

---

## Current Capabilities

✅ Wireless multi-sensor node with local display and alerts  
✅ Real-time motion detection and person classification  
✅ Anomaly detection on environmental patterns  
✅ Live web dashboard with historical charts and event logs  
✅ Local-only operation (no cloud dependencies)  

---

## Roadmap

### Phase 8 (In Progress)
- Sleep quality correlation using sensor-only pattern detection
- Gradient boosting models for environmental forecasting

### Phase 9 (Planned)
- Multi-node deployment (second Pico 2W in different room)
- Arduino Uno integration for additional sensor clusters
- LSTM-based time series forecasting
- Webhook/email alerting system

---

## Project Goals

This project serves dual purposes:
1. **Learning platform** for embedded systems, IoT protocols, edge ML, and full-stack integration
2. **Practical deployment** of a functional smart home monitoring system that respects privacy through local-only processing

Emphasis on:
- Building from first principles rather than using pre-built smart home platforms
- Understanding the full hardware-to-ML pipeline
- Iterative development with real-world deployment and feedback

---

## Setup & Deployment

### Hardware Requirements
- Raspberry Pi 4 (4GB+ recommended)
- Raspberry Pi Pico 2W
- Pi Camera Module or USB webcam
- Sensors: DHT11, BMP180, HC-SR501, GL5516, SW-520D
- Display: SH1107 128x64 OLED (I2C)
- Miscellaneous: breadboard, jumper wires, resistors, LEDs, buzzer, relay

### Software Installation
```bash
# Pi 4 setup
sudo apt update && sudo apt install mosquitto mosquitto-clients
pip install opencv-python tflite-runtime paho-mqtt streamlit torch pandas --break-system-packages

# Pico 2W setup
# Flash MicroPython .uf2, upload scripts via Thonny
```

Detailed setup instructions in `/docs/setup.md`

---

## Repository Structure
```
HomeEdge/
├── pico_node/          # MicroPython code for Pico 2W
│   ├── main.py
│   ├── sensors.py
│   ├── mqtt_client.py
│   └── config.py
├── pi_brain/           # Python code for Pi 4
│   ├── cv_motion.py
│   ├── tflite_detect.py
│   ├── anomaly_detector.py
│   ├── mqtt_logger.py
│   └── dashboard.py
├── models/             # Trained ML models
│   ├── autoencoder.pth
│   ├── ssd_mobilenet_v2.tflite
│   └── scaler.pkl
├── docs/               # Documentation
└── README.md
```

---

## License
MIT

---

## Acknowledgments
Inspired by industrial SCADA systems and a desire to understand IoT/ML systems from the ground up. Built iteratively with hands-on debugging of real hardware-software integration challenges.
