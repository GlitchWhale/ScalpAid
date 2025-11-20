import glob
import time
import RPi.GPIO as GPIO
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn


#GPIO pins
LED_PIN = 27
BUZZER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

#DS18B20 setup
BASE_DIR = '/sys/bus/w1/devices/'
DEVICE_FOLDER=glob.glob(BASE_DIR + '28*')[0]
DEVICE_FILE = DEVICE_FOLDER + '/w1_slave'

def read_temp_c():
    with open(DEVICE_FILE, 'r') as f:
        lines = f.readlines()

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        with open(DEVICE_FILE, 'r') as f:
            lines = f.readlines()

    pos = lines[1].find('t=')
    if pos != -1:
        temp_c = float(lines[1][pos+2:])/1000.0
        return temp_c
    return None

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
moisture_channel = AnalogIn(ads,0)

def read_moisture():
    """return tuple: (raw_value, voltage)"""
    return moisture_channel.value, moisture_channel.voltage


#pubnub setup
pnconfig = PNConfiguration()
pnconfig.publish_key = "pub-c-72867b34-4207-47de-a982-c35d4dbf14a8"
pnconfig.subscribe_key = "sub-c-965e4329-6565-4fba-bb02-05774be3a3c3"
pnconfig.uuid = "raspberrypi-1"

pubnub = PubNub(pnconfig)
CHANNEL = "scalp_data"

def publish(temp, state, moisture_raw, moisture_voltage):
    message={
        "device":"pi1",
        "temperature":temp,
        "state": state,
        "moisture_raw": moisture_raw,
        "moisture_voltage": moisture_voltage,
        "timestamp": int(time.time())
    }
    try:
        pubnub.publish().channel(CHANNEL).message(message).pn_async(lambda e, s: None)
        print("sent to pubnub:", message)
    except Exception as e:
        print("pubnub error:",e)

#thresholds
WARN_ON=29.5
WARN_OFF=29.2
ALARM_ON=30.2
ALARM_OFF=29.8

state="normal"
last_beep_toggle=0
beep_interval=0.25

try:
    while True:
        t=read_temp_c()
        if t is None:
            print("sensor read failure")
            time.sleep(0.5)
            continue

        moisture_raw, moisture_voltage= read_moisture()
        print(f"temperature: {t:.2f} C | Moisture V: {moisture_voltage:.3f} | state={state}")

#state logic
        if state == "normal":
            if t >= ALARM_ON:
                state="alarm"
            elif t >= WARN_ON:
                state="warn"

        elif state == "warn":
            if t >= ALARM_ON:
                state="alarm"
            elif t <= WARN_OFF:
                state="normal"

        elif state == "alarm":
            if t <= ALARM_OFF:
                state="warn" if t >= WARN_ON else "normal"


#output controls
        GPIO.output(LED_PIN, GPIO.HIGH if state in ("warn", "alarm") else GPIO.LOW)

        if state == "alarm":
            now = time.time()
            if now - last_beep_toggle >= beep_interval:
                GPIO.output(BUZZER_PIN, not GPIO.input(BUZZER_PIN))
                least_beep_toggle = now
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)

#publish to pubnub
        publish(t,state,moisture_raw,moisture_voltage)
        time.sleep(0.3)

except KeyboardInterrupt:
    print("stopped")
finally:
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()



