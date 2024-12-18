from lib.micropython_rfm9x import *
from machine import SPI, Pin, I2C
import struct
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data
from fusionmadgwick import Fusion
from lib.l86gps import L86GPS
from lib.lps22 import LPS22
import time
import os

# Initialize sensors
fuse = Fusion()
gps = L86GPS()
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
lps = LPS22(i2c)

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
        f.write("elapsed_time,temperature,pressure,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z\n")
    return log_file

def log_sensor_data(log_file, elapsed_time, pressure, accel, gyro):
    with open(log_file, "a") as f:
        # Assuming temperature is not available, using 0
        f.write(f"{elapsed_time},{0},{pressure},{accel[0]},{accel[1]},{accel[2]},{gyro[0]},{gyro[1]},{gyro[2]},0,0,0\n")

def encode_data(quaternions, gps_data, pressure):
    try:
        format_string = '<4f3ff'  # 4 quaternions, lat, lon, alt, pressure
        return struct.pack(format_string,
            quaternions[0], quaternions[1], quaternions[2], quaternions[3],
            gps_data['latitude'], gps_data['longitude'], gps_data['altitude'],
            pressure)
    except Exception as e:
        print(f"Encoding error: {e}")
        return None

def main():
    if read_who_am_i() != 0x67:
        print("ICM-42670-P not found.")
        return

    configure_sensor()
    
    # Initialize logging
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

                accel = read_accel_data()
                gyro = read_gyro_data()
                fuse.update_nomag(accel, gyro)
                
                gps_data = gps.read_gps()
                gps_values = {'latitude': 0.0, 'longitude': 0.0, 'altitude': 0.0}
                
                if gps_data and gps_data['type'] == 'GPGGA' and gps_data['status'] == 'valid':
                    gps_values = {
                        'latitude': gps_data['latitude'],
                        'longitude': gps_data['longitude'],
                        'altitude': gps_data['altitude']
                    }

                _, pressure = lps.get()
                
                # Log data to CSV
                log_sensor_data(log_file, elapsed_time, pressure, accel, gyro)
                
                # Transmit data
                data = encode_data(fuse.q, gps_values, pressure)
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
