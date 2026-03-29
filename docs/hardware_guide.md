# HomeEdge Hardware Guide

Complete wiring diagrams and hardware assembly instructions for all components.

## Table of Contents
1. [Component Overview](#component-overview)
2. [Pico 2W Wiring](#pico-2w-wiring)
3. [Pi 4 Wiring](#pi-4-wiring)
4. [Power Requirements](#power-requirements)
5. [PCB Layout Tips](#pcb-layout-tips)

---

## Component Overview

### Raspberry Pi Pico 2W Pinout Reference

```
                    Pico 2W
           ┌─────────────────────┐
    GP0  ──┤ 1  [ ]      [ ] 40 ├── VBUS (5V)
    GP1  ──┤ 2  [ ]      [ ] 39 ├── VSYS
    GND  ──┤ 3  [ ]      [ ] 38 ├── GND
    GP2  ──┤ 4  [ ]      [ ] 37 ├── 3V3_EN
    GP3  ──┤ 5  [ ]      [ ] 36 ├── 3V3(OUT)
    GP4  ──┤ 6  [S]      [D] 35 ├── ADC_VREF
    GP5  ──┤ 7  [C]      [ ] 34 ├── GP28 (A2)
    GND  ──┤ 8  [L]      [ ] 33 ├── GND
    GP6  ──┤ 9  [ ]      [A] 32 ├── GP27 (A1)
    GP7  ──┤10  [ ]      [D] 31 ├── GP26 (A0)
    GP8  ──┤11  [ ]      [C] 30 ├── RUN
    GP9  ──┤12  [ ]      [ ] 29 ├── GP22
    GND  ──┤13  [ ]      [ ] 28 ├── GND
    GP10 ──┤14  [ ]      [ ] 27 ├── GP21
    GP11 ──┤15  [ ]      [ ] 26 ├── GP20
    GP12 ──┤16  [ ]      [ ] 25 ├── GP19
    GP13 ──┤17  [ ]      [ ] 24 ├── GP18
    GND  ──┤18  [ ]      [ ] 23 ├── GND
    GP14 ──┤19  [ ]      [ ] 22 ├── GP17
    GP15 ──┤20  [ ]      [ ] 21 ├── GP16
           └─────────────────────┘

Legend:
[S][C][L] = SDA, SCL for I2C0 (default)
[A][D][C] = ADC pins (GP26-28)
```

### Raspberry Pi 4 GPIO Pinout (40-pin header)

```
3V3  ──┤ 1   2 ├── 5V
GP2  ──┤ 3   4 ├── 5V
GP3  ──┤ 5   6 ├── GND
GP4  ──┤ 7   8 ├── GP14 (TXD)
GND  ──┤ 9  10 ├── GP15 (RXD)
GP17 ──┤11  12 ├── GP18
GP27 ──┤13  14 ├── GND
GP22 ──┤15  16 ├── GP23
3V3  ──┤17  18 ├── GP24
GP10 ──┤19  20 ├── GND
GP9  ──┤21  22 ├── GP25
GP11 ──┤23  24 ├── GP8
GND  ──┤25  26 ├── GP7
ID_SD──┤27  28 ├── ID_SC
GP5  ──┤29  30 ├── GND
GP6  ──┤31  32 ├── GP12
GP13 ──┤33  34 ├── GND
GP19 ──┤35  36 ├── GP16
GP26 ──┤37  38 ├── GP20
GND  ──┤39  40 ├── GP21
```

---

## Pico 2W Wiring

### DHT11 Temperature & Humidity Sensor

**Connections:**
```
DHT11 Module          Pico 2W
────────────────────────────
VCC (3.3V)    ──→    3V3 (Pin 36)
GND           ──→    GND (Pin 38 or any GND)
DATA          ──→    GP28 (Pin 34)
```

**Notes:**
- Most DHT11 modules have built-in pull-up resistor
- If using bare sensor, add 10kΩ resistor between DATA and VCC
- Allow 2 seconds between readings
- First reading after power-on may be invalid

---

### BMP180 Barometric Pressure Sensor

**Connections:**
```
BMP180 Module         Pico 2W
────────────────────────────
VCC (3.3V)    ──→    3V3 (Pin 36)
GND           ──→    GND (Pin 38)
SDA           ──→    GP4 (Pin 6)
SCL           ──→    GP5 (Pin 7)
```

**I2C Bus:**
- Shares I2C0 bus with OLED display
- Default address: 0x77
- No pull-up resistors needed (built into module)

---

### HC-SR501 PIR Motion Sensor

**Connections:**
```
HC-SR501              Pico 2W
────────────────────────────
VCC (5V)      ──→    VBUS (Pin 40)  ⚠️ MUST BE 5V
GND           ──→    GND (Pin 38)
OUT           ──→    GP15 (Pin 20)
```

**Important:**
- ⚠️ **VBUS provides 5V from USB** — PIR requires 5V, won't work on 3.3V
- Output is 3.3V logic (safe for Pico GPIO)
- Warm-up time: 30-60 seconds after power-on
- Adjust sensitivity and hold-time with onboard potentiometers

**Potentiometer Settings:**
- Left pot: **Sensitivity** (distance range)
- Right pot: **Hold time** (how long output stays HIGH)

---

### GL5516 Photoresistor (Light Sensor)

**Voltage Divider Circuit:**
```
3.3V ──────┬──── Photoresistor ──┬──── 10kΩ Resistor ──── GND
           │                     │
           │                  GP26 (ADC0)
           │
```

**Connections:**
```
Component             Pico 2W
────────────────────────────
Photoresistor leg 1   ──→    3V3 (Pin 36)
Photoresistor leg 2   ──→    GP26 (Pin 31) AND 10kΩ to GND
10kΩ resistor         ──→    Between GP26 and GND
```

**Reading:**
- ADC value: 0 (dark) to 65535 (bright)
- Lower resistance in light → higher voltage at GP26
- Calibrate in your environment for best results

---

### SW-520D Tilt Switch

**Connections:**
```
SW-520D               Pico 2W
────────────────────────────
Pin 1         ──→    GP16 (Pin 21)
Pin 2         ──→    GND (Pin 23)
```

**In Code:**
```python
tilt = Pin(16, Pin.IN, Pin.PULL_UP)
```

**Notes:**
- Internal pull-up resistor enabled in software
- Reads LOW when tilted, HIGH when upright
- Metal ball inside closes circuit when level
- Debounce in software to avoid false triggers from vibrations

---

### SH1107 OLED Display (128x64, I2C)

**Connections:**
```
SH1107 Module         Pico 2W
────────────────────────────
VCC (3.3V)    ──→    3V3 (Pin 36)
GND           ──→    GND (Pin 38)
SDA           ──→    GP4 (Pin 6)
SCL           ──→    GP5 (Pin 7)
```

**I2C Configuration:**
- Shares I2C0 bus with BMP180
- Default address: 0x3C (check with I2C scanner)
- Some modules need jumper/switch set to I2C mode (vs SPI)

---

### Active Buzzer

**Connections:**
```
Active Buzzer         Pico 2W
────────────────────────────
VCC (+)       ──→    GP17 (Pin 22)
GND (-)       ──→    GND (Pin 23)
```

**Notes:**
- Active buzzer has internal oscillator (just apply voltage)
- If using 5V buzzer, connect VCC to VBUS and use a transistor to switch from GPIO
- 3.3V buzzer can connect directly to GPIO

---

### 5V Relay Module

**Connections:**
```
Relay Module          Pico 2W
────────────────────────────
VCC           ──→    VBUS (Pin 40) or 3.3V
GND           ──→    GND
IN (Signal)   ──→    GP14 (Pin 19)
```

**Load Connections (AC/DC device):**
```
Device        Relay Terminal
────────────────────────
Hot wire  ──→ NO (Normally Open)
Common    ──→ COM (Common)
NC not used
```

**Safety:**
- ⚠️ **Only use with low-voltage loads if you're not experienced with AC**
- Relay isolated device power from Pico
- Module may have LED indicator

---

### Push Buttons

**Button 1 (Arm/Disarm):**
```
Button                Pico 2W
────────────────────────────
Pin 1         ──→    GP18 (Pin 24)
Pin 2         ──→    GND (Pin 23)
```

**Button 2 (Acknowledge Alert):**
```
Button                Pico 2W
────────────────────────────
Pin 1         ──→    GP19 (Pin 25)
Pin 2         ──→    GND (Pin 23)
```

**In Code:**
```python
btn1 = Pin(18, Pin.IN, Pin.PULL_UP)
btn2 = Pin(19, Pin.IN, Pin.PULL_UP)
# Reads LOW when pressed, HIGH when released
```

**Optional External Pull-ups:**
If not using internal pull-ups, add 10kΩ resistors from each GPIO to 3.3V.

---

## Pi 4 Wiring

### Pi Camera Module

**Connection:**
1. Locate camera connector (between HDMI ports)
2. Gently pull up on the black plastic tab
3. Insert ribbon cable (blue side toward Ethernet port)
4. Push tab back down to lock

**Verify:**
```bash
libcamera-hello
```

### USB Webcam

Simply plug into any USB port. Check detection:
```bash
lsusb
v4l2-ctl --list-devices
```

---

## Power Requirements

### Pico 2W Power Budget

| Component | Current Draw |
|-----------|--------------|
| Pico 2W (idle) | ~30 mA |
| Pico 2W (WiFi) | ~150 mA peak |
| DHT11 | 2.5 mA |
| BMP180 | 5 µA idle, 1 mA active |
| HC-SR501 | 65 mA |
| SH1107 OLED | 20 mA |
| Buzzer | 30 mA |
| Relay | 70 mA |
| **Total Peak** | ~370 mA |

**Power Options:**
- USB power from computer/wall adapter (5V 1A minimum)
- External 5V supply to VSYS (regulated)
- Battery pack (ensure 5V regulated output)

### Pi 4 Power Budget

| Component | Current Draw |
|-----------|--------------|
| Pi 4 (idle) | ~600 mA |
| Pi 4 (load) | ~1200 mA |
| Pi Camera | 250 mA |
| USB Devices | Varies |
| **Recommended** | 5V 3A supply |

**Official Raspberry Pi power supply strongly recommended.**

---

## PCB Layout Tips

### Breadboard Organization

```
[Power Rails]
  Top:    3.3V (red), GND (blue)
  Bottom: 5V (red), GND (blue)

[Left Section]
  - Pico 2W
  - I2C devices (OLED, BMP180)
  - DHT11

[Center Section]
  - Buttons with pull-ups
  - Photoresistor divider

[Right Section]
  - Relay module
  - Buzzer
  - PIR sensor (with flying wires if needed)
```

### Wire Management
- Use different colors for power/ground/signal
- Keep I2C wires short and parallel
- Route high-current paths (relay, PIR) separately
- Label with masking tape if needed

### Common Mistakes to Avoid
❌ Connecting 5V to 3.3V pin → **Damage**  
❌ Forgetting PIR needs 5V → Won't work  
❌ Reversing SDA/SCL → I2C fails  
❌ No pull-up on DHT11 bare sensor → Unreliable  
❌ Sharing ground between different power supplies → Noise/instability  

---

## Testing Checklist

Before powering on full system:

- [ ] Verify all 3.3V connections go to 3V3 pin
- [ ] Verify all 5V connections go to VBUS
- [ ] Check no shorts between power and ground
- [ ] Double-check I2C wiring (SDA to SDA, SCL to SCL)
- [ ] Confirm PIR is on 5V, not 3.3V
- [ ] Test each sensor individually before combining

---

## Expansion Port Availability

### Available Pico GPIO After Core Sensors:
- GP0, GP1, GP2, GP3 — General purpose
- GP6-GP13 — General purpose
- GP20-GP22 — General purpose

**Future Use Cases:**
- Additional I2C devices (share GP4/GP5 bus)
- SPI devices (GP10-13)
- More buttons/LEDs
- Second DHT11 for different room
- Arduino Uno serial communication

### Available Pi 4 GPIO:
Most GPIO pins available if using camera via ribbon cable (not USB).

**Reserved:**
- I2C (GP2/GP3) if using ADC chip
- SPI (GP7-11) if using ADC chip

---

## Schematic Diagrams

*Note: For full schematics with component values and detailed layouts, see the `/images` folder in the repository or use tools like Fritzing to generate from the connections above.*

**Quick Reference Circuit:**
```
          Pico 2W
            ┌──────┐
      3V3 ──┤      ├─ GP28 ── DHT11
      GND ──┤      ├─ GP15 ── PIR
     VBUS ──┤      ├─ GP4  ── I2C SDA (OLED, BMP180)
      GND ──┤      ├─ GP5  ── I2C SCL
            └──────┘
```

---

## Troubleshooting Hardware Issues

### Sensor Returns 0 or Invalid Data
- Check power connections (multimeter: should read 3.3V or 5V)
- Verify GPIO pin number matches code
- Test sensor with known-good code first
- Check for loose connections

### I2C Device Not Detected
```python
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
print(hex(i2c.scan()))  # Should show [0x3c, 0x77]
```

If empty:
- Swap SDA/SCL
- Check both devices powered
- Verify pull-up resistors (usually built-in to modules)

### PIR Always Triggers or Never Triggers
- Wait 60 seconds after power-on for calibration
- Adjust sensitivity pot
- Check wiring (especially VBUS for 5V)
- Cover sensor dome to block light if in direct sun

### Buzzer Won't Sound
- Check polarity (+ to GPIO, - to GND)
- Verify it's an *active* buzzer (has internal oscillator)
- Try different GPIO pin
- Use multimeter to check voltage when activated

---

For additional help, see [setup.md](setup.md) or open an issue on GitHub.
