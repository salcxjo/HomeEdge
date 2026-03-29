"""
HomeEdge Pico 2W - Configuration File
Copy this file to config.py and edit with your settings
"""

# WiFi Settings
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

# MQTT Settings
MQTT_BROKER = "192.168.1.100"  # Your Raspberry Pi's local IP
MQTT_PORT = 1883
MQTT_CLIENT_ID = "homeedge_pico"

# GPIO Pin Assignments
DHT11_PIN = 28          # Temperature & humidity sensor
PIR_PIN = 15            # Motion sensor (HC-SR501)
TILT_PIN = 16           # Tamper/tilt switch (SW-520D)
BUZZER_PIN = 17         # Active buzzer
RELAY_PIN = 14          # Relay module
LIGHT_SENSOR_PIN = 26   # Photoresistor (ADC pin)

# I2C Configuration (for OLED and BMP180)
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400000       # 400kHz

# Sensor Reading Intervals (seconds)
SENSOR_INTERVAL = 10    # How often to read environmental sensors
HEARTBEAT_INTERVAL = 60 # How often to send status heartbeat

# Sensor Calibration
LIGHT_MIN = 100         # ADC value in darkness
LIGHT_MAX = 60000       # ADC value in bright light
