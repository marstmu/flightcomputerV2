from lib.micropython_rfm9x import *
from machine import SPI, Pin, I2C
import struct
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data, set_accel_scale, set_gyro_scale
from lib.fusionmadgwick import Fusion
from lib.l86gps import L86GPS
from lib.lps22 import LPS22
from micropython_mmc5603 import mmc5603
import time
import os

# Initialize sensors
fuse = Fusion()
gps = L86GPS()

# Initialize I2C buses
i2c_barometer = I2C(0, scl=Pin(9), sda=Pin(8))
i2c_magnetometer = I2C(0, sda=Pin(8), scl=Pin(9))
lps = LPS22(i2c_barometer)
mmc = mmc5603.MMC5603(i2c_magnetometer)

mag_x, mag_y, mag_z = mmc.magnetic
mx = mag_y
my = mag_z
mz = -1 * mag_x

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
                "gyro_x,gyro_y,gyro_z,mx,my,mz,gps_time,gps_date,gps_latitude,"
                "gps_longitude,gps_altitude,gps_satellites,gps_quality,gps_speed,"
                "gps_status,antenna_status,rssi\n")
    return log_file

def log_sensor_data(log_file, elapsed_time, temperature, pressure, accel, gyro, mag, gps_values, rssi):
    with open(log_file, "a") as f:
        f.write(f"{elapsed_time:.3f},{temperature},{pressure},"
                f"{accel[0]},{accel[1]},{accel[2]},"
                f"{gyro[0]},{gyro[1]},{gyro[2]},"
                f"{mag[0]},{mag[1]},{mag[2]},"
                f"{gps_values['time']},{gps_values['date']},"
                f"{gps_values['latitude']},{gps_values['longitude']},"
                f"{gps_values['altitude']},{gps_values['satellites']},"
                f"{gps_values['quality']},{gps_values['speed']},"
                f"{gps_values['status']},{gps_values['antenna_status']},{rssi}\n")

def encode_data(quaternions, gps_data, pressure, rssi):
    try:
        format_string = '<4f2i3ffi'  # 4 quaternions, time, satellites, lat, lon, alt, pressure, rssi
        return struct.pack(format_string,
            quaternions[0], quaternions[1], quaternions[2], quaternions[3],
            int(float(gps_data['time'])),  # Fixed conversion
            gps_data['satellites'],
            gps_data['latitude'], gps_data['longitude'], gps_data['altitude'],
            pressure, rssi)
    except Exception as e:
        print(f"Encoding error: {e}")
        return None

def main():
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

        while True:
            try:
                current_time = time.ticks_ms()
                elapsed_time = time.ticks_diff(current_time, start_time) / 1000

                # Read sensors
                accel = read_accel_data()
                gyro = read_gyro_data()
                mag = mmc.magnetic
                temperature = mmc.temperature
                _, pressure = lps.get()
                rssi = rfm9x.last_rssi

                fuse.update_nomag(accel, gyro)

                # Initialize GPS values with defaults
                gps_values = {
                    'time': '000000',
                    'date': '010100',
                    'latitude': 0.0,
                    'longitude': 0.0,
                    'altitude': 0.0,
                    'satellites': 0,
                    'quality': 'invalid',
                    'speed': 0.0,
                    'status': 'invalid',
                    'antenna_status': 'unknown'
                }

                # Read and process GPS data
                gps_data = gps.read_gps()
                if gps_data:
                    if gps_data['type'] == 'GPGGA' and gps_data['status'] == 'valid':
                        gps_values.update({
                            'time': gps_data['time'],
                            'latitude': gps_data['latitude'],
                            'longitude': gps_data['longitude'],
                            'altitude': gps_data['altitude'],
                            'satellites': gps_data['satellites'],
                            'quality': gps_data['quality'],
                            'status': gps_data['status']
                        })
                    elif gps_data['type'] == 'GPRMC' and gps_data['status'] == 'valid':
                        gps_values.update({
                            'speed': gps_data['speed'],
                            'date': gps_data['date']
                        })
                    elif gps_data['type'] == 'GPTXT':
                        gps_values['antenna_status'] = gps_data['antenna_status']

                # Log data
                log_sensor_data(log_file, elapsed_time, temperature, pressure,
                              accel, gyro, mag, gps_values, rssi)

                # Transmit data
                data = encode_data(fuse.q, gps_values, pressure, rssi)
                if data is not None:
                    rfm9x.send(data)
                    print("Data packet sent")

                time.sleep(0.05)

            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(1)

    except Exception as e:
        print(f"Radio initialization error: {e}")

if __name__ == "__main__":
    main()
