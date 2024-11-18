from time import sleep
from machine import I2C, Pin
from lps22 import LPS22

i2c = I2C(0, scl=Pin(9), sda=Pin(8))

lps = LPS22(i2c)

while True:
    try:
        temperature, pressure = lps.get()
        print("Temperature: {:.2f} °C".format(temperature))
        print("Pressure: {:.2f} hPa".format(pressure))
    except Exception as e:
        print("Error reading from sensor:", e)
    
    sleep(1)

