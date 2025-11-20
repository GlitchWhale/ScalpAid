
import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS1115(i2c)

chan= AnalogIn(ads, 0)

print("reading moisture")

while True:
    value = chan.value
    voltage = chan.voltage

    print(f"raw:{value}|voltage:{voltage:.3f}V")
    time.sleep(0.5)
