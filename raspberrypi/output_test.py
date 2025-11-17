import RPi.GPIO as GPIO
import time

#pin setup
LED_PIN = 27
BUZZER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    print("testing LED...")
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(LED_PIN, GPIO.LOW)
    print("LED test complete...")

    print("testing Buzzer...")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    print("Buzzer test complete...")

    print("both together...")
    for i in range(5):
        GPIO.output(LED_PIN, GPIO.HIGH)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)

    print("output test finished...")

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
    print("GPIO cleaned")
