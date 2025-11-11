# ScalpAid

ScalpAid is an IoT-based scalp health monitoring system developed as part of the SD3B IoT coursework.  
It uses a Raspberry Pi to collect temperature and moisture data from the scalp and sends it to a cloud backend for analysis and real-time visualization using PubNub.

---

## Project Overview

ScalpAid monitors scalp conditions using two key sensors:
- DS18B20 temperature sensor  
- Capacitive soil moisture sensor (through ADS1115 ADC)

The Raspberry Pi reads data from these sensors, triggers a piezo buzzer alert when moisture is low, and transmits the readings to a Flask-based backend server.  
The backend stores the data and broadcasts it via PubNub for real-time updates.

---

## Hardware Components

| Component | Function | Connection |
|------------|-----------|-------------|
| Raspberry Pi | Central controller | I²C + GPIO |
| DS18B20 | Temperature sensor | 1-Wire (GPIO4 by default) |
| Capacitive Moisture Sensor | Moisture detection | Analog via ADS1115 |
| ADS1115 | 16-bit ADC for analog sensor | I²C (SDA, SCL) |
| Piezo Buzzer | Audio feedback for alerts | Digital GPIO17 |
| Power Bank | Power supply for portability | USB |

---
