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
```

---

## LinkedIn Post (3 Variants — Pick Your Tone)

### Option 1 — Technical & Detailed
```
I've been building HomeEdge over the past few months — a local-first smart home monitoring system that combines embedded sensing, computer vision, and custom edge ML models.

The system runs on a Raspberry Pi 4 (central node) and Pico 2W (wireless sensor node), communicating over MQTT. Key capabilities:

🔹 Real-time environmental monitoring (temp, humidity, pressure, light)
🔹 Motion detection + TensorFlow Lite person classification
🔹 Custom PyTorch autoencoder for anomaly detection on sensor data
🔹 Live Streamlit dashboard — all processing happens locally, no cloud

Tech stack: MicroPython, OpenCV, TFLite, PyTorch, MQTT, SQLite

This started as a learning project to understand the full IoT/ML pipeline from GPIO-level sensor interfacing to model deployment. It's also become a genuinely useful deployment running 24/7 in my home.

Next phase: expanding to multi-node sensing and exploring time-series forecasting with LSTMs.

Code + documentation: [GitHub link]

#EmbeddedSystems #MachineLearning #IoT #EdgeComputing #ComputerVision
```

### Option 2 — Balanced & Accessible
```
Spent the last few months building HomeEdge — a smart home monitoring system that runs entirely on local hardware.

Two devices talk to each other: a Raspberry Pi Pico 2W wirelessly transmits sensor data (temperature, motion, light levels) to a Raspberry Pi 4 that runs computer vision and machine learning models to detect people and flag unusual environmental patterns.

Everything runs locally — no cloud, no subscriptions, no data leaving the network.

Why build this? I wanted to learn embedded systems, computer vision, and edge ML from first principles rather than using pre-built platforms. It's been an incredible learning experience debugging real hardware, training models on my own data, and deploying a system that actually runs reliably.

The project is ongoing — currently expanding the ML capabilities and adding more sensor nodes.

GitHub: [link]

#IoT #MachineLearning #SmartHome #RaspberryPi #ProjectBuild
```

### Option 3 — Story-Focused
```
I've always been fascinated by how industrial monitoring systems work — the kind you see in factories or power plants with sensor arrays and real-time dashboards.

So I built a miniature version for my home.

HomeEdge combines a wireless sensor node (Raspberry Pi Pico 2W) with a central processing unit (Raspberry Pi 4) running computer vision and custom ML models. It monitors temperature, humidity, motion, and light — then uses a PyTorch autoencoder I trained on my own data to flag when conditions are unusual.

The whole thing runs locally. No cloud. No subscriptions. Just hardware communicating over MQTT and models running inference on a $50 computer.

It started as a way to learn embedded systems and edge ML. It's become a genuinely useful deployment that's been running 24/7 for weeks.

Next: adding more nodes, Arduino integration, and time-series forecasting.

Full writeup + code: [GitHub link]

#BuildInPublic #MachineLearning #IoT #EmbeddedSystems
```

---

## Resume Entry

### Under "Projects" or "Personal Projects" Section:
```
HomeEdge — Local Edge Intelligence System | Sep 2024 – Present
- Developed a distributed IoT monitoring system integrating embedded sensing (Raspberry Pi Pico 2W, MicroPython), computer vision (OpenCV, TensorFlow Lite), and custom ML models (PyTorch) for real-time anomaly detection on environmental data
- Implemented MQTT-based telemetry architecture with six concurrent sensor streams (temperature, humidity, pressure, motion, light, tamper) published wirelessly to central broker
- Deployed TFLite MobileNet SSD for on-device person detection with confidence-thresholded inference on Raspberry Pi 4 CPU
- Trained and deployed PyTorch autoencoder for anomaly detection on environmental patterns, achieving real-time inference with sub-100ms latency on edge hardware
- Built full-stack monitoring dashboard (Streamlit, SQLite) with live camera feed, historical sensor charts, and event logging accessible on local network
- Technologies: Python, MicroPython, OpenCV, TensorFlow Lite, PyTorch, MQTT, I2C/SPI/ADC hardware interfacing, SQLite
```

**Alternative shorter version if space is tight:**
```
HomeEdge — Smart Home Monitoring System | Sep 2024 – Present
- Built distributed IoT system with wireless sensor nodes (Pico 2W) and edge ML pipeline (Pi 4) for environmental monitoring and computer vision-based person detection
- Trained custom PyTorch autoencoder on local sensor data for real-time anomaly detection; deployed TFLite models for on-device inference
- Tech: Python, MicroPython, OpenCV, TensorFlow Lite, PyTorch, MQTT, embedded hardware (I2C/SPI/GPIO)
