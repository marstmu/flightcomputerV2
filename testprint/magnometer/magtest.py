import time
from machine import Pin, I2C
from micropython_mmc5603 import mmc5603

i2c = I2C(0, sda=Pin(8), scl=Pin(9))
mmc = mmc5603.MMC5603(i2c)

while True:
    mag_x, mag_y, mag_z = mmc.magnetic
    print(f"X:{mag_x:.2f}, Y:{mag_y:.2f}, Z:{mag_z:.2f} uT")
    temp = mmc.temperature
    print(f"Temperature: {temp:.2f}°C")
    print()
    time.sleep(0.10)
