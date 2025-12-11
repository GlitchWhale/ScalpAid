import glob
import time
import RPi.GPIO as GPIO
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from pubnub.callbacks import SubscribeCallback

# GPIO pins
LED_PIN = 27
BUZZER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

# DS18B20 setup
BASE_DIR = '/sys/bus/w1/devices/'
DEVICE_FOLDER = glob.glob(BASE_DIR + '28*')[0]
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
        temp_c = float(lines[1][pos+2:]) / 1000.0
        return temp_c
    return None

# moisture / ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
moisture_channel = AnalogIn(ads, 0)

DRY_RAW = 17824
WET_RAW = 5280

def moisture_to_percent(raw):
    percent = (DRY_RAW - raw) / (DRY_RAW - WET_RAW)
    percent = max(0, min(percent, 1))
    return round(percent * 100, 1)

def read_moisture():
    raw = moisture_channel.value
    voltage = moisture_channel.voltage
    percent = moisture_to_percent(raw)
    return raw, voltage, percent

# PubNub setup
pnconfig = PNConfiguration()
pnconfig.publish_key = "pub-c-72867b34-4207-47de-a982-c35d4dbf14a8"
pnconfig.subscribe_key = "sub-c-965e4329-6565-4fba-bb02-05774be3a3c3"
pnconfig.uuid = "raspberrypi-1"

pubnub = PubNub(pnconfig)
DATA_CHANNEL = "scalp_data"
COMMAND_CHANNEL = "scalp_commands"

start_reading = False

class CommandListener(SubscribeCallback):
    def message(self, pubnub, event):
        global start_reading
        msg = event.message

        if msg.get("command") == "start":
            print("Received start")
            start_reading = True

        if msg.get("command") == "stop":
            print("Received stop")
            start_reading = False

pubnub.add_listener(CommandListener())
pubnub.subscribe().channels(COMMAND_CHANNEL).execute()

def publish(temp, state, moisture_raw, moisture_voltage, percent):
    message = {
        "device": "pi1",
        "temperature": temp,
        "state": state,
        "moisture_raw": moisture_raw,
        "moisture_voltage": moisture_voltage,
        "moisture_percent": percent,
        "timestamp": int(time.time())
    }
    try:
        pubnub.publish().channel(DATA_CHANNEL).message(message).pn_async(lambda e, s: None)
        print("sent to pubnub:", message)
    except Exception as e:
        print("pubnub error:", e)

# thresholds
WARN_ON = 29.5
WARN_OFF = 29.2
ALARM_ON = 30.2
ALARM_OFF = 29.8

state = "normal"
last_beep_toggle = 0
beep_interval = 0.25

# how often to read sensors / publish
SAMPLE_INTERVAL = 5.0   
IDLE_INTERVAL = 1.0

try:
    while True:

        if not start_reading:
            GPIO.output(LED_PIN, GPIO.LOW)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(IDLE_INTERVAL)
            continue

        t = read_temp_c()
        if t is None:
            print("sensor read failure")
            time.sleep(SAMPLE_INTERVAL)
            continue

        moisture_raw, moisture_voltage, moisture_percent = read_moisture()
        print(
            f"Temp: {t:.2f} C | "
            f"Moisture: {moisture_percent}% | "
            f"(raw={moisture_raw}, V={moisture_voltage:.3f}) | "
            f"State={state}"
        )

        # state logic
        if state == "normal":
            if t >= ALARM_ON:
                state = "alarm"
            elif t >= WARN_ON:
                state = "warn"

        elif state == "warn":
            if t >= ALARM_ON:
                state = "alarm"
            elif t <= WARN_OFF:
                state = "normal"

        elif state == "alarm":
            if t <= ALARM_OFF:
                state = "warn" if t >= WARN_ON else "normal"

        # output controls
        GPIO.output(LED_PIN, GPIO.HIGH if state in ("warn", "alarm") else GPIO.LOW)

        if state == "alarm":
            now = time.time()
            if now - last_beep_toggle >= beep_interval:
                GPIO.output(BUZZER_PIN, not GPIO.input(BUZZER_PIN))
                last_beep_toggle = now
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)

        # publish to pubnub
        publish(t, state, moisture_raw, moisture_voltage, moisture_percent)

        # main sampling delay
        time.sleep(SAMPLE_INTERVAL)

except KeyboardInterrupt:
    print("stopped")
finally:
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()
