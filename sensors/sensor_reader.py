import time
import Adafruit_ADS1x15
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
MOISTURE_CHANNEL = 0   # A0 input on ADS1115
buzzer_pin = 17        # GPIO17 (physical pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.output(buzzer_pin, GPIO.LOW)

temp_sensor = W1ThermSensor()

def read_temperature():
    """Read DS18B20 temperature in °C."""
    try:
        return round(temp_sensor.get_temperature(), 2)
    except Exception as e:
        print("[Temp Error]", e)
        return None

def read_moisture():
    """Read raw moisture sensor value (0-32767)."""
    try:
        return adc.read_adc(MOISTURE_CHANNEL, gain=GAIN)
    except Exception as e:
        print("[Moisture Error]", e)
        return None

def alert_buzzer(state):
    """Turn buzzer on (True) or off (False)."""
    GPIO.output(buzzer_pin, GPIO.HIGH if state else GPIO.LOW)

def get_sensor_data():
    """Combine all readings into a dict."""
    temp = read_temperature()
    moisture = read_moisture()

    # Example: trigger buzzer if scalp is too dry (< threshold)
    if moisture is not None and moisture < 2000:
        alert_buzzer(True)
    else:
        alert_buzzer(False)

    return {
        "device_id": "pi_headband_01",
        "temperature": temp,
        "moisture": moisture,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    try:
        while True:
            data = get_sensor_data()
            print(data)
            time.sleep(2)
    except KeyboardInterrupt:
        GPIO.cleanup()