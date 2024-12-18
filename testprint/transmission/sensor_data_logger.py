import os
import time
from machine import I2C, Pin
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data, set_accel_scale, set_gyro_scale
from lps22 import LPS22
from micropython_mmc5603 import mmc5603

# Initialize peripherals
# Barometer
i2c_barometer = I2C(0, scl=Pin(9), sda=Pin(8))
lps = LPS22(i2c_barometer)

# IMU
if read_who_am_i() == 0x67:
    configure_sensor()
    set_accel_scale(3) # ±16g
    set_gyro_scale(1) # ±500 dps
else:
    print("IMU not detected. Check wiring!")

# Magnetometer
i2c_magnetometer = I2C(0, sda=Pin(8), scl=Pin(9))
mmc = mmc5603.MMC5603(i2c_magnetometer)

def log_data(elapsed_time, data_dir):
    log_file = f"{data_dir}/sensor_log.csv"
    
    # Read barometer
    try:
        _, pressure_hPa = lps.get()
    except Exception as e:
        pressure_hPa = None
        print("Barometer error:", e)
    
    # Read IMU
    try:
        accel = read_accel_data()
        gyro = read_gyro_data()
    except Exception as e:
        accel, gyro = (None, None, None), (None, None, None)
        print("IMU error:", e)
    
    # Read magnetometer and temperature
    try:
        mag_x, mag_y, mag_z = mmc.magnetic
        temperature = mmc.temperature
    except Exception as e:
        mag_x, mag_y, mag_z = None, None, None
        temperature = None
        print("Magnetometer error:", e)
    
    # Write data to log file with 3 decimal places for elapsed time
    with open(log_file, "a") as f:
        f.write(f"{elapsed_time:.3f},{temperature},{pressure_hPa},{accel[0]},{accel[1]},{accel[2]},{gyro[0]},{gyro[1]},{gyro[2]},{mag_x},{mag_y},{mag_z}\n")

