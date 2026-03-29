"""
HomeEdge Raspberry Pi 4 - Configuration File
Copy this file to config.py and edit with your settings
"""

import os

# MQTT Settings
MQTT_BROKER = "localhost"  # Or Pi's IP if accessing remotely
MQTT_PORT = 1883
MQTT_TOPICS = [
    "home/pico/temperature",
    "home/pico/humidity",
    "home/pico/pressure",
    "home/pico/light_level",
    "home/pico/motion",
    "home/pico/tamper",
    "home/pico/armed",
    "home/pico/status"
]

# Database Settings
DB_PATH = os.path.expanduser("~/HomeEdge/homedata.db")

# Camera Settings
CAMERA_INDEX = 0  # 0 for USB webcam, adjust for Pi Camera
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 15

# Motion Detection Settings
MOTION_THRESHOLD = 500  # Minimum contour area to trigger
MOTION_PERCENT_THRESHOLD = 2.0  # Minimum % of frame in motion

# TFLite Model Settings
TFLITE_MODEL_PATH = os.path.expanduser("~/HomeEdge/models/ssd_mobilenet_v2.tflite")
TFLITE_LABELS_PATH = os.path.expanduser("~/HomeEdge/models/labelmap.txt")
CONFIDENCE_THRESHOLD = 0.5
PERSON_CLASS_ID = 1  # COCO dataset person class

# Anomaly Detection Settings
ANOMALY_MODEL_PATH = os.path.expanduser("~/HomeEdge/models/autoencoder.pth")
ANOMALY_SCALER_PATH = os.path.expanduser("~/HomeEdge/models/scaler.pkl")
ANOMALY_THRESHOLD_PATH = os.path.expanduser("~/HomeEdge/models/threshold.txt")

# File Paths
MOTION_FRAMES_DIR = os.path.expanduser("~/HomeEdge/motion_frames")
PERSON_DETECTIONS_DIR = os.path.expanduser("~/HomeEdge/person_detections")

# Create directories if they don't exist
os.makedirs(MOTION_FRAMES_DIR, exist_ok=True)
os.makedirs(PERSON_DETECTIONS_DIR, exist_ok=True)

# Dashboard Settings
DASHBOARD_PORT = 8501
DASHBOARD_UPDATE_INTERVAL = 5  # seconds

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
