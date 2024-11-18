from time import sleep
from machine import I2C, Pin
from lps22 import LPS22

# Configure I2C with SCL on GPIO9 and SDA on GPIO8
i2c = I2C(0, scl=Pin(9), sda=Pin(8))

# Initialize the LPS22 sensor
lps = LPS22(i2c)

# Read and print temperature and pressure in a loop
while True:
    try:
        temperature, pressure = lps.get()
        print("Temperature: {:.2f} °C".format(temperature))
        print("Pressure: {:.2f} hPa".format(pressure))
    except Exception as e:
        print("Error reading from sensor:", e)
    
    # Wait for a second before the next reading
    sleep(1)

