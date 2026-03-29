"""
HomeEdge Pico 2W - Sensor Reading Functions
"""

from machine import Pin, ADC
import dht
import time
from config import *

# Initialize sensors
dht_sensor = dht.DHT11(Pin(DHT11_PIN))
pir_sensor = Pin(PIR_PIN, Pin.IN)
tilt_sensor = Pin(TILT_PIN, Pin.IN, Pin.PULL_UP)
light_adc = ADC(LIGHT_SENSOR_PIN)

def read_dht11():
    """
    Read temperature and humidity from DHT11
    Returns: (temperature_C, humidity_percent) or (None, None) on error
    """
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temp, humidity
    except Exception as e:
        print(f'DHT11 error: {e}')
        return None, None

def read_bmp180(i2c):
    """
    Read pressure and temperature from BMP180
    Returns: (pressure_hPa, temperature_C) or (None, None) on error
    
    Note: Requires BMP180 library to be uploaded to Pico
    """
    try:
        # Import BMP180 driver (must be in lib/)
        from bmp180 import BMP180
        bmp = BMP180(i2c)
        bmp.oversample_sett = 2
        bmp.baseline = 101325  # Sea level pressure
        
        pressure = bmp.pressure / 100  # Convert Pa to hPa
        temp = bmp.temperature
        
        return pressure, temp
    except Exception as e:
        print(f'BMP180 error: {e}')
        return None, None

def read_pir():
    """
    Read PIR motion sensor state
    Returns: True if motion detected, False otherwise
    """
    return pir_sensor.value() == 1

def read_light_sensor():
    """
    Read photoresistor light level
    Returns: Light level as percentage (0-100)
    """
    raw = light_adc.read_u16()
    
    # Map to 0-100% range
    light_percent = ((raw - LIGHT_MIN) / (LIGHT_MAX - LIGHT_MIN)) * 100
    light_percent = max(0, min(100, light_percent))  # Clamp to 0-100
    
    return round(light_percent, 1)

def read_tilt_switch():
    """
    Read tilt switch state
    Returns: True if tilted (tamper), False if upright
    """
    # Active low (reads 0 when tilted)
    return tilt_sensor.value() == 0
