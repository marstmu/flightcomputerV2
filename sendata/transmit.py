from micropython_rfm9x import *
from machine import SPI, Pin
import struct
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data
from fusionmadgwick import Fusion
import time

# Initialize Fusion object
fuse = Fusion()

def encode_quaternions(quaternions):
    try:
        # Ensure quaternions is a tuple of 4 values
        if len(quaternions) != 4:
            raise ValueError("Quaternions must have 4 values")
        return struct.pack('ffff', *quaternions)
    except Exception as e:
        print(f"Encoding error: {e}")
        return None

def main():
    # Initialize sensor
    if read_who_am_i() != 0x67:
        print("ICM-42670-P not found.")
        return
        
    print("ICM-42670-P detected.")
    configure_sensor()

    # Initialize radio
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
                # Read sensor data
                accel = read_accel_data()
                gyro = read_gyro_data()
                
                # Update fusion
                fuse.update_nomag(accel, gyro)
                
                # Encode quaternions
                data = encode_quaternions(fuse.q)
                if data is not None:
                    rfm9x.send(data)
                    print("Sent quaternions:", fuse.q)
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"Radio initialization error: {e}")

if __name__ == "__main__":
    main()
