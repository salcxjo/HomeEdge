# HomeEdge Setup Guide

This guide walks through the complete setup process for HomeEdge, from hardware assembly to software deployment.

## Table of Contents
1. [Hardware Assembly](#hardware-assembly)
2. [Raspberry Pi 4 Setup](#raspberry-pi-4-setup)
3. [Raspberry Pi Pico 2W Setup](#raspberry-pi-pico-2w-setup)
4. [Network Configuration](#network-configuration)
5. [Testing & Verification](#testing--verification)
6. [Troubleshooting](#troubleshooting)

---

## Hardware Assembly

### Tools Needed
- Breadboard
- Jumper wires (M-M, M-F, F-F)
- Multimeter (optional but helpful)
- Soldering iron (if using headers)

### Important Safety Notes
⚠️ **Always power off devices before wiring**  
⚠️ **Double-check power connections (3.3V vs 5V)**  
⚠️ **HC-SR501 PIR requires 5V (use VBUS on Pico)**  
⚠️ **Never connect 5V directly to Pico GPIO pins**

---

## Raspberry Pi 4 Setup

### 1. Install Operating System

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash **Raspberry Pi OS (64-bit)** to microSD card (32GB+ recommended)
3. During setup:
   - Enable SSH
   - Configure WiFi credentials
   - Set hostname (e.g., `homeedge-pi`)
   - Set username and password

4. Insert SD card and boot Pi 4

### 2. Initial Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git vim tmux

# Set timezone
sudo timedatectl set-timezone America/Edmonton  # Adjust to your timezone

# Enable camera (if using Pi Camera Module)
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Enable SPI (if using ADC chip later)
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable

# Reboot
sudo reboot
```

### 3. Install MQTT Broker

```bash
# Install Mosquitto
sudo apt install -y mosquitto mosquitto-clients

# Create configuration file
sudo nano /etc/mosquitto/conf.d/local.conf
```

Add the following:
```
listener 1883
allow_anonymous true
protocol mqtt
```

```bash
# Restart Mosquitto
sudo systemctl restart mosquitto

# Enable on boot
sudo systemctl enable mosquitto

# Verify it's running
sudo systemctl status mosquitto
```

### 4. Test MQTT Locally

Open two terminal windows:

**Terminal 1 (Subscriber):**
```bash
mosquitto_sub -v -t "test/#"
```

**Terminal 2 (Publisher):**
```bash
mosquitto_pub -t "test/hello" -m "world"
```

You should see `test/hello world` appear in Terminal 1.

### 5. Install Python Dependencies

```bash
# Navigate to project directory
cd ~
git clone https://github.com/yourusername/HomeEdge.git
cd HomeEdge

# Install Python packages
pip install -r requirements_pi.txt --break-system-packages
```

**Note:** `--break-system-packages` is needed on newer Raspberry Pi OS versions that use externally-managed Python environments.

### 6. Download TFLite Model

```bash
cd ~/HomeEdge/models

# Download MobileNet SSD v2 COCO model
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip

# Extract
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip

# Rename for consistency
mv detect.tflite ssd_mobilenet_v2.tflite
```

### 7. Configure Settings

```bash
cd ~/HomeEdge/pi_brain
cp config.example.py config.py
nano config.py
```

Edit with your specific settings:
- MQTT broker IP (use `localhost` or Pi's IP)
- Database path
- Camera index
- Model paths

### 8. Create Database

```bash
cd ~/HomeEdge/pi_brain
python3 mqtt_logger.py
```

This will create the SQLite database and tables. Press Ctrl+C after a few seconds.

---

## Raspberry Pi Pico 2W Setup

### 1. Flash MicroPython Firmware

1. Download the **Pico 2W** specific firmware from [micropython.org](https://micropython.org/download/RPI_PICO2_W/)
   - **Important:** Use Pico **2W** firmware, not regular Pico firmware
   
2. Hold the **BOOTSEL** button on the Pico while plugging it into USB

3. Pico mounts as a USB drive named `RPI-RP2`

4. Drag and drop the `.uf2` file onto the drive

5. Pico automatically reboots with MicroPython installed

### 2. Install Thonny IDE

On your development machine (or the Pi):

```bash
sudo apt install thonny
```

Or download from [thonny.org](https://thonny.org/)

### 3. Configure Thonny

1. Open Thonny
2. Go to **Tools > Options > Interpreter**
3. Select **MicroPython (Raspberry Pi Pico)**
4. Select the correct port (e.g., `/dev/ttyACM0`)
5. Click OK

### 4. Test Connection

In Thonny's shell, type:
```python
print("Hello from Pico 2W!")
```

You should see the output immediately.

### 5. Install Required Libraries

Download these MicroPython libraries:

**DHT11 Driver:**
```python
# In Thonny, create a new file and paste:
# https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/sensor/dht/dht.py
# Save as: lib/dht.py on the Pico
```

**SH1107 OLED Driver:**
Download from a community source (search "micropython sh1107") and save to `lib/sh1107.py`

**umqtt.simple** (usually pre-installed):
Test by running:
```python
from umqtt.simple import MQTTClient
```

If it errors, install from [micropython-lib](https://github.com/micropython/micropython-lib).

### 6. Upload Project Files

1. In Thonny, open each file from `pico_node/` directory
2. Use **File > Save As** and choose **Raspberry Pi Pico**
3. Save with the same filename

Upload in this order:
- `config.example.py` → rename to `config.py` and edit
- `sensors.py`
- `display.py`
- `mqtt_client.py`
- `main.py`

### 7. Configure WiFi and MQTT

Edit `config.py` on the Pico:

```python
# WiFi Settings
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

# MQTT Settings
MQTT_BROKER = "192.168.1.100"  # Your Pi's IP address
MQTT_PORT = 1883

# GPIO Pin Assignments (adjust if wired differently)
DHT11_PIN = 28
PIR_PIN = 15
TILT_PIN = 16
BUZZER_PIN = 17
RELAY_PIN = 14
LIGHT_SENSOR_PIN = 26

I2C_SDA = 4
I2C_SCL = 5

# Timing
SENSOR_INTERVAL = 10
HEARTBEAT_INTERVAL = 60
```

### 8. Test Individual Components

Before running the full system, test each sensor:

**Test DHT11:**
```python
from machine import Pin
import dht

sensor = dht.DHT11(Pin(28))
sensor.measure()
print(f"Temp: {sensor.temperature()}°C, Humidity: {sensor.humidity()}%")
```

**Test PIR:**
```python
from machine import Pin
import time

pir = Pin(15, Pin.IN)
while True:
    print(f"PIR: {pir.value()}")
    time.sleep(0.5)
```

**Test OLED:**
```python
from machine import I2C, Pin
from sh1107 import SH1107_I2C

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled = SH1107_I2C(128, 64, i2c)
oled.text("Hello!", 0, 0)
oled.show()
```

### 9. Run Main Script

Once all components test successfully:

1. Press the **Stop** button in Thonny to reset
2. Click **Run > Run current script** on `main.py`
3. Watch the OLED display and Thonny console for status

The Pico should:
- Connect to WiFi (OLED shows status)
- Connect to MQTT broker
- Begin reading sensors
- Display readings on OLED
- Publish to MQTT topics

---

## Network Configuration

### Find Your Pi's IP Address

```bash
hostname -I
```

Note this IP — you'll need it for:
- Pico's MQTT broker configuration
- Accessing the dashboard from other devices

### Configure Firewall (if enabled)

```bash
# Allow MQTT
sudo ufw allow 1883/tcp

# Allow Streamlit dashboard
sudo ufw allow 8501/tcp

# Check status
sudo ufw status
```

### Static IP (Recommended)

To prevent the Pi's IP from changing:

**Method 1: Router DHCP Reservation**
- Access your router settings
- Find DHCP settings
- Reserve an IP for the Pi's MAC address

**Method 2: Static IP on Pi**
```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Reboot: `sudo reboot`

---

## Testing & Verification

### 1. Verify MQTT Communication

On the Pi, subscribe to all topics:
```bash
mosquitto_sub -v -t "home/#"
```

You should see messages from the Pico appearing every 10 seconds:
```
home/pico/temperature {"temperature": 22.4, "unit": "C"}
home/pico/humidity {"humidity": 58, "unit": "%"}
home/pico/pressure {"pressure": 1013.25, "unit": "hPa"}
...
```

### 2. Test Camera

```bash
cd ~/HomeEdge/pi_brain
python3 cv_motion.py
```

A window should open showing the camera feed with motion detection overlays. Walk in front of the camera to test.

Press 'q' to quit.

### 3. Test TFLite Person Detection

```bash
python3 tflite_detect.py
```

This runs inference on any saved motion frames. Check console output for detection results.

### 4. Launch Dashboard

```bash
streamlit run dashboard.py --server.address 0.0.0.0
```

Access from any device on the network at `http://<pi_ip>:8501`

You should see:
- Current sensor readings
- Live camera feed
- Historical charts
- Event log

### 5. End-to-End Test

1. Start all services:
   ```bash
   # Terminal 1
   python3 mqtt_logger.py
   
   # Terminal 2
   python3 cv_motion.py
   
   # Terminal 3
   streamlit run dashboard.py --server.address 0.0.0.0
   ```

2. Walk in front of camera
3. Check dashboard for:
   - Motion event logged
   - Person detection event (if you're in frame)
   - Sensor data updating

---

## Troubleshooting

### Pico Won't Connect to WiFi

**Check:**
- SSID and password are correct in `config.py`
- WiFi network is 2.4GHz (Pico 2W doesn't support 5GHz)
- Network is not hidden or using unusual security

**Debug:**
Add print statements to `main.py`:
```python
print(f"Connecting to {WIFI_SSID}...")
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while not wlan.isconnected():
    print(".", end="")
    time.sleep(1)
print(f"Connected! IP: {wlan.ifconfig()[0]}")
```

### Pico Connects to WiFi But Not MQTT

**Check:**
- MQTT broker IP is correct (use Pi's local IP, not `localhost`)
- Mosquitto is running on Pi: `sudo systemctl status mosquitto`
- Firewall allows port 1883

**Test from another machine:**
```bash
mosquitto_pub -h <pi_ip> -t "test" -m "hello"
```

### DHT11 Returns Invalid Readings

**Common issues:**
- Sensor needs 1-2 second delay between reads
- Wiring: VCC→3.3V, GND→GND, DATA→GPIO with 10kΩ pull-up (some modules have built-in pull-up)
- Try a different GPIO pin

### OLED Display Not Working

**Check:**
- I2C address is correct (usually `0x3C`)
- Run I2C scanner:
```python
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
print(i2c.scan())  # Should show [60] (0x3C in hex)
```

### Camera Not Detected

**Pi Camera Module:**
```bash
libcamera-hello
```

If it fails:
- Check ribbon cable connection (blue side toward Ethernet port)
- Enable camera in `raspi-config`
- Update firmware: `sudo rpi-update`

**USB Webcam:**
```bash
v4l2-ctl --list-devices
ls /dev/video*
```

Adjust `CAMERA_INDEX` in `config.py` if needed.

### TFLite Import Error

```bash
# Check installation
pip show tflite-runtime

# If missing
pip install tflite-runtime --break-system-packages

# Or use full TensorFlow (larger but works)
pip install tensorflow --break-system-packages
```

Then change import in code:
```python
# from tflite_runtime.interpreter import Interpreter
from tensorflow.lite import Interpreter  # If using full TF
```

### Dashboard Won't Load

**Check:**
- Streamlit is running: `ps aux | grep streamlit`
- Port 8501 is not blocked by firewall
- Access using Pi's IP, not localhost, from other devices
- Try accessing from Pi itself first: `http://localhost:8501`

### High CPU Usage

This is normal for computer vision workload. To reduce:
- Lower camera resolution in `cv_motion.py`
- Reduce inference frequency (process every Nth frame)
- Disable dashboard auto-refresh when not actively viewing

### Database Growing Too Large

```bash
# Check size
du -h ~/HomeEdge/homedata.db

# Vacuum to reclaim space
sqlite3 ~/HomeEdge/homedata.db "VACUUM;"

# Delete old data (keep last 30 days)
sqlite3 ~/HomeEdge/homedata.db "DELETE FROM sensor_data WHERE timestamp < $(date -d '30 days ago' +%s);"
```

---

## Running as System Services

To have everything start automatically on boot, create systemd service files:

```bash
sudo nano /etc/systemd/system/homeedge-logger.service
```

```ini
[Unit]
Description=HomeEdge MQTT Logger
After=network.target mosquitto.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/HomeEdge/pi_brain
ExecStart=/usr/bin/python3 mqtt_logger.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable homeedge-logger.service
sudo systemctl start homeedge-logger.service
```

Repeat for other services (cv_motion, dashboard, etc.)

---

## Next Steps

Once everything is working:
1. Let the system collect data for 2–4 weeks
2. Train the anomaly detection model (see [ml_training.md](ml_training.md))
3. Explore Phase 8+ features
4. Consider adding more sensor nodes

For more help, see the other documentation files or open an issue on GitHub.
