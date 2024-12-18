import time
from machine import Pin, I2C
from micropython_mmc5603 import mmc5603

i2c = I2C(0, sda=Pin(8), scl=Pin(9))
mmc = mmc5603.MMC5603(i2c)

while True:
    mag_x, mag_y, mag_z = mmc.magnetic
    
    mz = -1 * mag_x
    mx = mag_y
    my = mag_z
    
    print(f"X:{mx:.2f}, Y:{my:.2f}, Z:{mz:.2f} uT")
    temp = mmc.temperature
    print(f"Temperature: {temp:.2f}°C")
    print()
    time.sleep(0.10)
    
