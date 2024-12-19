from lib.micropython_rfm9x import *
from machine import SPI, Pin, I2C
import struct
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data, set_accel_scale, set_gyro_scale
from gyrolib import MadgwickFilter, MovingAverageFilter
from lib.l86gps import L86GPS
from lib.lps22 import LPS22
from micropython_mmc5603 import mmc5603
import time
import os
import asyncio

# Initialize sensors
madgwick = MadgwickFilter(beta=0.03)
maf = MovingAverageFilter(window_size=12)
gps = L86GPS()

# Initialize I2C buses
i2c_barometer = I2C(0, scl=Pin(9), sda=Pin(8))
i2c_magnetometer = I2C(0, sda=Pin(8), scl=Pin(9))
lps = LPS22(i2c_barometer)
mmc = mmc5603.MMC5603(i2c_magnetometer)

# Initial magnetometer readings
mag_x, mag_y, mag_z = mmc.magnetic
mx = mag_y
my = mag_z
mz = -1 * mag_x

# Global variables
current_gps_values = {
    'latitude': 0.0,
    'longitude': 0.0,
    'altitude': 0.0,
    'satellites': 0,
    'status': 'invalid'
}
start_time = 0
log_file = None

def create_directory_if_needed(directory):
    try:
        if directory not in os.listdir("/"):
            print(f"Creating directory: {directory}")
            os.mkdir(directory)
    except Exception as e:
        print(f"Error creating directory: {e}")

def initialize_log_file(data_dir):
    log_file = f"{data_dir}/sensor_log.csv"
    with open(log_file, "w") as f:
        f.write("elapsed_time,temperature,pressure,accel_x,accel_y,accel_z,"
                "gyro_x,gyro_y,gyro_z,mx,my,mz,gps_latitude,gps_longitude,"
                "gps_altitude,gps_satellites,gps_status\n")
    return log_file

def log_sensor_data(log_file, elapsed_time, temperature, pressure, accel, gyro, mag, gps_values):
    with open(log_file, "a") as f:
        f.write(f"{elapsed_time:.3f},{temperature},{pressure},"
                f"{accel[0]},{accel[1]},{accel[2]},"
                f"{gyro[0]},{gyro[1]},{gyro[2]},"
                f"{mag[0]},{mag[1]},{mag[2]},"
                f"{gps_values['latitude']},{gps_values['longitude']},"
                f"{gps_values['altitude']},{gps_values['satellites']},"
                f"{gps_values['status']}\n")

def encode_data(quaternion, gps_data, pressure):
    try:
        format_string = '<4f3fif'  # 4 quaternions, lat, lon, alt, satellites (int), pressure
        return struct.pack(format_string,
            quaternion.w, quaternion.x, quaternion.y, quaternion.z,
            gps_data['latitude'], gps_data['longitude'], gps_data['altitude'],
            gps_data['satellites'],
            pressure)
    except Exception as e:
        print(f"Encoding error: {e}")
        return None

async def read_gps_task():
    global current_gps_values
    while True:
        try:
            gps_data = gps.read_gps()
            if gps_data and gps_data['type'] == 'GPGGA' and gps_data['status'] == 'valid':
                current_gps_values = {
                    'latitude': gps_data['latitude'],
                    'longitude': gps_data['longitude'],
                    'altitude': gps_data['altitude'],
                    'satellites': gps_data.get('satellites', 0),
                    'status': gps_data['status']
                }
        except Exception as e:
            print(f"GPS task error: {e}")
        await asyncio.sleep_ms(100)  # Check GPS every 100ms

async def sensor_task(rfm9x):
    global current_gps_values, start_time, log_file
    last_time = time.ticks_ms()
    
    while True:
        try:
            current_time = time.ticks_ms()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            elapsed_time = time.ticks_diff(current_time, start_time) / 1000

            # Read sensors
            accel = read_accel_data()
            gyro = read_gyro_data()
            mag = mmc.magnetic
            temperature = mmc.temperature
            _, pressure = lps.get()

            # Update orientation
            madgwick.update(gyro, accel, dt)
            smoothed_quaternion = maf.apply(madgwick.q)

            # Log data
            log_sensor_data(log_file, elapsed_time, temperature, pressure,
                          accel, gyro, mag, current_gps_values)

            # Transmit data
            data = encode_data(smoothed_quaternion, current_gps_values, pressure)
            if data is not None:
                rfm9x.send(data)
                print("Data packet sent")

            await asyncio.sleep_ms(50)  # 50ms delay between sensor readings

        except Exception as e:
            print(f"Sensor task error: {e}")
            await asyncio.sleep_ms(1000)

async def main():
    global start_time, log_file
    
    if read_who_am_i() != 0x67:
        print("ICM-42670-P not found.")
        return

    configure_sensor()
    set_accel_scale(3)  # ±16g
    set_gyro_scale(1)   # ±500 dps

    data_dir = "logs"
    create_directory_if_needed(data_dir)
    log_file = initialize_log_file(data_dir)
    start_time = time.ticks_ms()

    try:
        # Initialize radio
        CS = Pin(20, Pin.OUT)
        RESET = Pin(17, Pin.OUT)
        spi = SPI(0,
            baudrate=1000000,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SPI.MSB,
            sck=Pin(18),
            mosi=Pin(19),
            miso=Pin(16))

        rfm9x = RFM9x(spi, CS, RESET, 915.0)
        rfm9x.tx_power = 14
        rfm9x.signal_bandwidth = 500000
        rfm9x.coding_rate = 5
        rfm9x.spreading_factor = 9
        rfm9x.enable_crc = True

        # Create and run tasks
        gps_task = asyncio.create_task(read_gps_task())
        sensors_task = asyncio.create_task(sensor_task(rfm9x))
        
        await asyncio.gather(gps_task, sensors_task)

    except Exception as e:
        print(f"Main task error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

