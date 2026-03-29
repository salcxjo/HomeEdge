# HomeEdge System Architecture

Detailed technical architecture and design decisions.

## Table of Contents
1. [System Overview](#system-overview)
2. [Communication Architecture](#communication-architecture)
3. [Data Flow](#data-flow)
4. [Technology Choices](#technology-choices)
5. [Scalability Considerations](#scalability-considerations)

---

## System Overview

HomeEdge is a distributed IoT system with three main layers:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Streamlit Dashboard (Port 8501)                      │  │
│  │  - Real-time sensor charts                            │  │
│  │  - Camera feed display                                │  │
│  │  - Event log viewer                                   │  │
│  │  - Anomaly alerts                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTP (local network)
                            │
┌─────────────────────────────────────────────────────────────┐
│              Processing & Intelligence Layer                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Raspberry Pi 4                                       │  │
│  │  ├─ MQTT Broker (Mosquitto)                          │  │
│  │  ├─ MQTT Logger → SQLite                             │  │
│  │  ├─ OpenCV Motion Detection                          │  │
│  │  ├─ TFLite Person Detection                          │  │
│  │  ├─ PyTorch Anomaly Detection                        │  │
│  │  └─ Streamlit Server                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ MQTT (TCP/IP)
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Sensor/Edge Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Raspberry Pi Pico 2W                                 │  │
│  │  ├─ WiFi Connection                                   │  │
│  │  ├─ Sensor Reading (I2C, ADC, GPIO)                  │  │
│  │  ├─ MQTT Publishing                                   │  │
│  │  ├─ Local Display (SH1107 OLED)                      │  │
│  │  └─ Physical Controls (buttons, buzzer, relay)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Communication Architecture

### MQTT Pub/Sub Model

```
Pico 2W (Publisher)                 Pi 4 (Subscriber)
      │                                   │
      ├─ home/pico/temperature ─────────>├─ MQTT Logger
      ├─ home/pico/humidity ────────────>├─ Dashboard
      ├─ home/pico/pressure ────────────>├─ Anomaly Detector
      ├─ home/pico/light_level ─────────>│
      ├─ home/pico/motion ──────────────>│
      ├─ home/pico/tamper ──────────────>│
      ├─ home/pico/armed ───────────────>│
      └─ home/pico/status ──────────────>│
```

**Topic Naming Convention:**
```
home/{device}/{data_type}
```

**Message Format (JSON):**
```json
{
  "value": 22.4,
  "unit": "C",
  "timestamp": 1710000000  // Optional
}
```

### Quality of Service (QoS)

- **QoS 0** (At most once): Used for high-frequency sensor data
  - Acceptable to lose occasional readings
  - Lower overhead
  
- **QoS 1** (At least once): Used for alerts and events
  - Critical messages (person detected, tamper alert)
  - Delivery confirmation required

---

## Data Flow

### Sensor Data Pipeline

```
1. Pico reads DHT11 every 10s
        ↓
2. Formats as JSON: {"temperature": 22.4, "unit": "C"}
        ↓
3. Publishes to: home/pico/temperature
        ↓
4. Pi MQTT Logger receives message
        ↓
5. Writes to SQLite: (timestamp, topic, value)
        ↓
6. Dashboard queries SQLite every 5s
        ↓
7. Displays chart to user
```

### Computer Vision Pipeline

```
1. Pi Camera captures frame (640x480)
        ↓
2. OpenCV applies MOG2 background subtraction
        ↓
3. Find contours in foreground mask
        ↓
4. Filter by area threshold (> 500px)
        ↓
5. If motion detected:
   ├─ Save frame to /motion_frames/
   ├─ Resize to 300x300 for TFLite
   ├─ Run MobileNet SSD inference
   ├─ Parse detections
   └─ If person (class 1) with confidence > 0.5:
      ├─ Log event to database
      ├─ Publish to home/pi/person_detected
      └─ Save frame with bounding box
```

### Anomaly Detection Pipeline

```
1. Collect sensor readings in buffer
        ↓
2. Every 60s, aggregate latest values
        ↓
3. Normalize using trained scaler
        ↓
4. Feed to autoencoder
        ↓
5. Calculate reconstruction error (MSE)
        ↓
6. Compare to threshold (95th percentile)
        ↓
7. If error > threshold:
   ├─ Log anomaly event
   ├─ Publish to home/pi/anomaly_detected
   └─ Trigger alert on dashboard
```

---

## Technology Choices

### Why MicroPython on Pico?
- **Rapid prototyping** vs C/C++ (no compile cycle)
- **Built-in WiFi support** on Pico 2W
- **Easy sensor libraries** (DHT, I2C)
- **Trade-off:** Slower than C, but sufficient for 10s sensor intervals

### Why MQTT?
- **Lightweight** (runs on Pi zero/Pico)
- **Pub/sub decoupling** (easy to add subscribers)
- **Standard protocol** (interoperable with other systems)
- **Local broker** (no cloud dependency)

### Why SQLite?
- **Embedded database** (no separate server)
- **Good enough performance** for time-series logging
- **Easy backup** (single file)
- **Query flexibility** vs CSV/JSON files

### Why TFLite over PyTorch for Person Detection?
- **Optimized for edge** (CPU-only inference)
- **Smaller model size** (quantized INT8)
- **Faster inference** (~100ms vs 500ms for full PyTorch)
- **Lower memory footprint**

### Why PyTorch for Anomaly Detection?
- **Custom model training** (autoencoder not available pre-trained)
- **Research-friendly** (easier to experiment)
- **Can quantize after training** if needed
- **Acceptable inference time** (~50ms every 60s)

### Why Streamlit?
- **Rapid dashboard development** (Python-native)
- **Built-in components** (charts, tables, forms)
- **Real-time updates** via session state
- **Low barrier to entry** vs Flask/Django

---

## Scalability Considerations

### Current Limitations

1. **Single MQTT Broker**
   - All nodes depend on one Pi 4
   - Solution: Add broker redundancy or use external broker

2. **SQLite Write Concurrency**
   - Single writer at a time
   - Not an issue at current scale (~6 writes/10s)
   - Future: Migrate to PostgreSQL if multiple high-frequency nodes

3. **Pi 4 CPU Load**
   - OpenCV + TFLite + PyTorch + Streamlit = ~60-80% CPU
   - Solution: Offload camera processing to separate Pi or reduce frame rate

4. **WiFi Reliability**
   - Pico 2W on 2.4GHz only
   - Range limited (~30m indoors)
   - Solution: Add WiFi extender or use wired Ethernet for Pi

### Scaling to Multiple Nodes

**Current (1 Pico):**
```
home/pico/temperature
home/pico/humidity
...
```

**Scaled (N Picos):**
```
home/bedroom/pico/temperature
home/living_room/pico/temperature
home/garage/pico/temperature
...
```

**Dashboard Changes:**
- Room selector dropdown
- Per-room charts
- Cross-room correlation analysis

### Future Architecture: Edge ML Distribution

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Pico + Pico  │     │ Pico + Pico  │     │ Pico + Pico  │
│   (Room 1)   │     │   (Room 2)   │     │   (Room 3)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                      MQTT Broker
                            │
       ┌────────────────────┴────────────────────┐
       │                                         │
   ┌───▼────┐                              ┌────▼────┐
   │  Pi 4  │                              │  Pi 4   │
   │ Camera │                              │  ML     │
   │  Node  │                              │  Node   │
   └────────┘                              └─────────┘
```

**Benefits:**
- Dedicated compute per task
- Fault isolation
- Parallel processing

---

## Security Considerations

### Current (Local Network Only)

- **MQTT:** No authentication (allow_anonymous true)
- **Dashboard:** No login required
- **Database:** No encryption

**Acceptable because:**
- All traffic stays on local network
- No internet exposure
- Physical access required

### If Internet-Exposed (Future)

**Required changes:**
1. **MQTT Authentication**
   - Username/password per client
   - TLS encryption (port 8883)

2. **Dashboard Authentication**
   - streamlit-authenticator library
   - Or reverse proxy with basic auth

3. **Database Encryption**
   - SQLCipher for encrypted SQLite
   - Or full disk encryption

4. **Network Segmentation**
   - IoT devices on separate VLAN
   - Firewall rules limiting Pi access

---

## Monitoring & Observability

### Current Logging

- **Pico:** Print to serial console (Thonny)
- **Pi:** Python print statements
- **MQTT:** `mosquitto_sub -v -t "home/#"`

### Production-Ready Logging (Future)

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/homeedge.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Track

- MQTT message rate (messages/second)
- Camera frame rate (FPS)
- ML inference latency (ms)
- Database size growth (MB/day)
- CPU/memory usage
- WiFi signal strength (RSSI)

---

## Disaster Recovery

### Backup Strategy

**Daily:**
```bash
# Copy SQLite database
cp ~/HomeEdge/homedata.db ~/HomeEdge/backups/homedata_$(date +%Y%m%d).db

# Retain last 30 days
find ~/HomeEdge/backups/ -name "*.db" -mtime +30 -delete
```

**Weekly:**
```bash
# Backup entire repository
tar -czf ~/HomeEdge_backup_$(date +%Y%m%d).tar.gz ~/HomeEdge/
```

### Recovery Procedures

**Pico Failure:**
1. Flash new Pico with MicroPython
2. Upload code from GitHub
3. Update config.py with WiFi/MQTT settings
4. Deploy and verify MQTT messages

**Pi Failure:**
1. Flash new SD card with Pi OS
2. Install dependencies: `pip install -r requirements_pi.txt`
3. Restore database from latest backup
4. Deploy code from GitHub
5. Restart services

---

For implementation details, see other documentation files.
