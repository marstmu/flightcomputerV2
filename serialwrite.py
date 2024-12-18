from lib.micropython_rfm9x import *
from machine import SPI, Pin, I2C
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data, set_accel_scale, set_gyro_scale
from lib.fusionmadgwick import Fusion
from lib.l86gps import L86GPS
from lib.lps22 import LPS22
from micropython_mmc5603 import mmc5603
import time
import sys

# Initialize sensors
fuse = Fusion()
gps = L86GPS()

# Initialize I2C buses
i2c_barometer = I2C(0, scl=Pin(9), sda=Pin(8))
i2c_magnetometer = I2C(0, sda=Pin(8), scl=Pin(9))
lps = LPS22(i2c_barometer)
mmc = mmc5603.MMC5603(i2c_magnetometer)

def main():
    if read_who_am_i() != 0x67:
        print("ICM-42670-P not found.")
        return

    # Configure IMU with specific scales
    configure_sensor()
    set_accel_scale(3)  # ±16g
    set_gyro_scale(1)   # ±500 dps

    # Store last valid GPS values
    last_longitude = 0.0
    last_latitude = 0.0
    last_altitude = 0.0
    last_satellites = 0

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

        while True:
            try:
                # Read sensors
                accel = read_accel_data()
                gyro = read_gyro_data()
                _, pressure = lps.get()
                
                # Update fusion without magnetometer
                fuse.update_nomag(accel, gyro)
                
                # Read GPS
                gps_data = gps.read_gps()
                
                # Update GPS values if valid
                if gps_data and gps_data['type'] == 'GPGGA' and gps_data['status'] == 'valid':
                    last_longitude = gps_data['longitude']
                    last_latitude = gps_data['latitude']
                    last_altitude = gps_data['altitude']
                    last_satellites = gps_data.get('satellites', 0)
                
                # Get RSSI
                rssi = rfm9x.rssi
                
                # Print data in specified order using last valid GPS values
                sys.stdout.write(f"{fuse.q[0]},{fuse.q[1]},{fuse.q[2]},{fuse.q[3]},"
                               f"{last_longitude},{last_latitude},{last_altitude},"
                               f"{last_satellites},{pressure},{rssi}\n")
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"Radio initialization error: {e}")

if __name__ == "__main__":
    main()

