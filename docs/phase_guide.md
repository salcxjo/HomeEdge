# HomeEdge Development Phases

This document outlines the iterative development approach taken for HomeEdge, from initial prototyping to advanced ML features.

---

## Overview

HomeEdge was built in phases, with each phase adding new capabilities while maintaining stability of previous work. This approach allowed for:
- Incremental testing and debugging
- Learning new technologies progressively
- Maintaining a working system throughout development
- Clear milestone-based progress tracking

---

## Phase 1 — Pico 2W Core Node (Complete)

**Goal:** Build a wireless sensor node that reliably transmits environmental data over MQTT.

**Components:**
- Raspberry Pi Pico 2W
- DHT11 (temp & humidity)
- HC-SR501 (PIR motion)
- SH1107 OLED display
- Push buttons for control
- Relay module
- Active buzzer

**Key Learnings:**
- MicroPython firmware installation and debugging
- I2C, GPIO, and ADC interfacing
- MQTT pub/sub architecture
- WiFi fault tolerance and reconnection logic
- Local feedback via OLED display

**Deliverables:**
- Fully functional wireless sensor node
- MQTT messages publishing every 10 seconds
- Local display showing sensor readings
- Physical controls for arm/disarm

**Duration:** ~2 weeks

---

## Phase 2 — Pi Camera + OpenCV (Complete)

**Goal:** Add computer vision capabilities with real-time motion detection.

**Components:**
- Raspberry Pi 4
- Pi Camera Module (or USB webcam)
- OpenCV library

**Key Learnings:**
- Camera interfacing (libcamera vs legacy stack)
- Background subtraction algorithms (MOG2)
- Contour detection and filtering
- Frame rate optimization on CPU-only hardware

**Deliverables:**
- Live camera feed with motion detection overlays
- Motion-triggered frame saving
- Configurable sensitivity thresholds

**Duration:** ~1 week

---

## Phase 3 — TFLite Person Detection (Complete)

**Goal:** Add machine learning inference to classify detected motion as person vs. other.

**Components:**
- MobileNet SSD v2 (TFLite format)
- TFLite runtime

**Key Learnings:**
- Model quantization for edge deployment
- Input tensor preprocessing (resize, normalize, color space)
- Output parsing (bounding boxes, class IDs, confidence scores)
- Inference optimization for CPU-only execution

**Deliverables:**
- Person detection running on motion-flagged frames
- Confidence-thresholded alerts
- Event logging with detection metadata

**Duration:** ~1 week

---

## Phase 4 — Streamlit Dashboard (Complete)

**Goal:** Create a web-based interface for monitoring and visualization.

**Components:**
- Streamlit framework
- SQLite database
- Plotly for charts

**Key Learnings:**
- Real-time data streaming in web apps
- Database design for time-series sensor data
- Interactive visualization techniques
- Network-accessible deployment

**Deliverables:**
- Live dashboard accessible from any device on network
- Historical sensor charts (temp, humidity)
- Event log with timestamps
- Camera feed integration

**Duration:** ~1 week

---

## Phase 5 — Expanded Sensing (Complete)

**Goal:** Add more sensors to enrich environmental data.

**New Components:**
- BMP180 (pressure sensor)
- GL5516 (photoresistor)
- SW-520D (tilt switch)
- Active buzzer for alerts

**Key Learnings:**
- I2C bus sharing between multiple devices
- ADC-based analog sensor reading
- Voltage divider circuits for resistive sensors
- Event-driven alerts vs. continuous monitoring

**Deliverables:**
- Six concurrent data streams from Pico
- Barometric pressure and light level charts
- Tamper detection with buzzer alerts
- Richer dataset for ML training

**Duration:** ~1 week

---

## Phase 6 — Physical Control Panel (Skipped)

**Original Goal:** Build a hardware control interface on the Pi side.

**Planned Components:**
- Potentiometers for threshold tuning
- LED status indicators
- IR receiver for remote control

**Decision:** Skipped this phase to focus on ML development. May revisit later.

---

## Phase 7 — Edge ML & Anomaly Detection (Complete)

**Goal:** Train a custom model on collected sensor data for anomaly detection.

**Components:**
- PyTorch for model training
- Scikit-learn for preprocessing
- SHAP for model interpretation (optional)

**Key Learnings:**
- Autoencoder architecture for unsupervised anomaly detection
- Feature normalization and scaling
- Threshold determination from validation set
- Real-time inference integration with MQTT pipeline

**Deliverables:**
- Trained autoencoder on 2+ weeks of local data
- Real-time anomaly flagging
- Dashboard visualization of reconstruction error
- Event-driven alerts on anomalies

**Duration:** ~2 weeks (including data collection time)

---

## Phase 8 — Sleep Correlation (Planned)

**Goal:** Correlate environmental conditions with sleep quality metrics.

**Approach:**
- Sensor-only sleep pattern detection (no wearable required)
- Motion cessation + light level as sleep proxy
- Gradient boosting model to predict sleep quality
- Dashboard section for sleep insights

**Status:** On hold pending sufficient baseline data collection.

---

## Phase 9 — Multi-Node Expansion (Planned)

**Goal:** Deploy multiple sensor nodes across different rooms.

**Components:**
- Additional Pico 2W units
- Different sensor configurations per room
- Centralized data aggregation on Pi

**Challenges:**
- MQTT topic namespace design
- Inter-node time synchronization
- Cross-room correlation analysis

---

## Phase 10 — Arduino Integration (Future)

**Goal:** Integrate Arduino Uno for comparison and expansion.

**Potential Use Cases:**
- Serial communication bridge to Pi
- C++ vs MicroPython performance comparison
- Low-power always-on monitoring
- SPI-heavy sensor clusters

---

## Development Principles

Throughout all phases, these principles guided development:

1. **Working code first, optimization later** — Get it functional before making it fast
2. **Test components individually** — Never debug multiple new things simultaneously
3. **Incremental commits** — Small, tested changes rather than big rewrites
4. **Documentation alongside code** — README and comments written during development
5. **Real-world deployment** — Run in production to find edge cases
6. **Learn by doing** — Build from first principles rather than copy-paste

---

## Lessons Learned

### Hardware
- PIR sensors need proper warm-up time (60+ seconds)
- I2C pull-ups are usually built into breakout boards
- Always verify power requirements (3.3V vs 5V) before connecting
- Breadboard connections can be unreliable — check with multimeter

### Software
- MQTT reconnection logic is essential for reliability
- Normalize features before feeding to neural networks
- Background subtraction needs tuning per environment
- Database writes should be batched for performance

### ML
- Need 2+ weeks of diverse data before training makes sense
- Anomaly thresholds are highly environment-specific
- Model quantization matters significantly for edge devices
- Autoencoder bottleneck size is the key tuning parameter

### Integration
- Each layer (hardware, MQTT, database, ML, dashboard) should be testable independently
- Logging is worth the effort — critical for debugging
- Configuration files prevent hardcoding mistakes
- Systemd services are the right way to run background processes

---

## Time Investment

| Phase | Duration | Effort Level |
|-------|----------|--------------|
| Phase 1 | 2 weeks | High (new to MicroPython) |
| Phase 2 | 1 week | Medium |
| Phase 3 | 1 week | Medium-High (TFLite learning curve) |
| Phase 4 | 1 week | Low-Medium (Streamlit is easy) |
| Phase 5 | 1 week | Low (reusing patterns) |
| Phase 7 | 2 weeks | High (ML theory + data collection) |
| **Total** | **8 weeks** | Intermittent work, not full-time |

---

## What's Next?

Current active development:
- Phase 8 exploration (sensor-only sleep detection)
- Performance optimization (reduce CPU load)
- Documentation improvements
- Arduino Uno integration experiments

Community contributions welcome!

---

For detailed technical implementation of each phase, see the other documentation files.
