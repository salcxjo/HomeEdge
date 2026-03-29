"""
HomeEdge Pico 2W - Main Loop
Coordinates all sensors, display, and MQTT communication
"""

from machine import Pin, I2C, ADC
import time
import network
import json
from umqtt.simple import MQTTClient

# Import project modules
from config import *
from sensors import read_dht11, read_bmp180, read_pir, read_light_sensor, read_tilt_switch
from display import init_display, update_display
from mqtt_client import connect_mqtt, publish_data

# Initialize hardware
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = init_display(i2c)
buzzer = Pin(BUZZER_PIN, Pin.OUT)
relay = Pin(RELAY_PIN, Pin.OUT)

# Initialize buttons
btn_arm = Pin(18, Pin.IN, Pin.PULL_UP)
btn_ack = Pin(19, Pin.IN, Pin.PULL_UP)

# State variables
armed = False
last_sensor_read = 0
last_heartbeat = 0

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f'Connecting to WiFi: {WIFI_SSID}...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout = 0
        while not wlan.isconnected() and timeout < 20:
            time.sleep(1)
            timeout += 1
        
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print(f'Connected! IP: {ip}')
            return True, ip
        else:
            print('WiFi connection failed')
            return False, None
    else:
        return True, wlan.ifconfig()[0]

def handle_buttons():
    """Check button states and handle presses"""
    global armed
    
    # Arm/Disarm button
    if btn_arm.value() == 0:  # Pressed (active low)
        armed = not armed
        print(f'Armed: {armed}')
        time.sleep(0.3)  # Debounce
        return 'armed', armed
    
    # Acknowledge button
    if btn_ack.value() == 0:
        print('Alert acknowledged')
        buzzer.value(0)  # Turn off buzzer
        time.sleep(0.3)
        return 'acknowledge', True
    
    return None, None

def trigger_alert(alert_type):
    """Trigger buzzer and relay on alert"""
    if armed:
        if alert_type == 'motion':
            # Short beep
            buzzer.value(1)
            time.sleep(0.1)
            buzzer.value(0)
        elif alert_type == 'person':
            # Three short beeps
            for _ in range(3):
                buzzer.value(1)
                time.sleep(0.1)
                buzzer.value(0)
                time.sleep(0.1)
        elif alert_type == 'tamper':
            # Continuous beep
            buzzer.value(1)
        
        # Activate relay
        relay.value(1)

def main():
    """Main program loop"""
    global last_sensor_read, last_heartbeat, armed
    
    # Connect to WiFi
    wifi_connected, ip = connect_wifi()
    if not wifi_connected:
        print('ERROR: Cannot proceed without WiFi')
        return
    
    # Connect to MQTT broker
    client = connect_mqtt(MQTT_BROKER, MQTT_PORT)
    if client is None:
        print('ERROR: Cannot connect to MQTT broker')
        return
    
    print('HomeEdge Pico Node Starting...')
    
    # Sensor data buffer
    sensor_data = {
        'temperature': 0,
        'humidity': 0,
        'pressure': 0,
        'light_level': 0,
        'motion': False,
        'tamper': False,
        'armed': armed
    }
    
    while True:
        try:
            current_time = time.time()
            
            # Read sensors at specified interval
            if current_time - last_sensor_read >= SENSOR_INTERVAL:
                # Read environmental sensors
                temp, humidity = read_dht11()
                if temp is not None:
                    sensor_data['temperature'] = temp
                    sensor_data['humidity'] = humidity
                
                pressure, _ = read_bmp180(i2c)
                if pressure is not None:
                    sensor_data['pressure'] = pressure
                
                light_level = read_light_sensor()
                sensor_data['light_level'] = light_level
                
                # Publish sensor data
                publish_data(client, 'home/pico/temperature', 
                           {'temperature': sensor_data['temperature'], 'unit': 'C'})
                publish_data(client, 'home/pico/humidity',
                           {'humidity': sensor_data['humidity'], 'unit': '%'})
                publish_data(client, 'home/pico/pressure',
                           {'pressure': sensor_data['pressure'], 'unit': 'hPa'})
                publish_data(client, 'home/pico/light_level',
                           {'light': sensor_data['light_level'], 'unit': '%'})
                
                last_sensor_read = current_time
            
            # Check motion and tamper sensors (fast polling)
            motion = read_pir()
            if motion != sensor_data['motion']:
                sensor_data['motion'] = motion
                publish_data(client, 'home/pico/motion', {'motion': motion})
                if motion:
                    trigger_alert('motion')
            
            tamper = read_tilt_switch()
            if tamper != sensor_data['tamper']:
                sensor_data['tamper'] = tamper
                publish_data(client, 'home/pico/tamper', {'tamper': tamper})
                if tamper:
                    trigger_alert('tamper')
            
            # Handle button presses
            event, value = handle_buttons()
            if event == 'armed':
                sensor_data['armed'] = value
                publish_data(client, 'home/pico/armed', {'armed': value})
            
            # Update OLED display
            update_display(oled, sensor_data)
            
            # Send heartbeat
            if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
                publish_data(client, 'home/pico/status', 
                           {'status': 'online', 'uptime': current_time})
                last_heartbeat = current_time
            
            time.sleep(0.1)  # Small delay to prevent busy-wait
            
        except KeyboardInterrupt:
            print('Shutting down...')
            buzzer.value(0)
            relay.value(0)
            client.disconnect()
            break
        except Exception as e:
            print(f'Error in main loop: {e}')
            time.sleep(1)

if __name__ == '__main__':
    main()
