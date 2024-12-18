from micropython_rfm9x import *
from machine import SPI, Pin
import struct
import time
import sys

# Global variables to store last valid data
last_valid_data = {
    'quaternions': [0, 0, 0, 0],
    'latitude': 0,
    'longitude': 0,
    'altitude': 0,
    'satellites': 0,
    'pressure': 0,
    'valid': False
}

def decode_data(data):
    try:
        format_string = '<4f3fif'  # 4 quaternions, lat, lon, alt, satellites (int), pressure
        values = struct.unpack(format_string, data)
        return {
            'quaternions': values[0:4],
            'latitude': values[4],
            'longitude': values[5],
            'altitude': values[6],
            'satellites': values[7],
            'pressure': values[8]
        }
    except Exception as e:
        sys.stdout.write(f"Decoding error: {e}\n")
        return None

def update_valid_data(data):
    if data['satellites'] > 0 and data['satellites'] < 100:
        last_valid_data['quaternions'] = data['quaternions']
        last_valid_data['latitude'] = data['latitude']
        last_valid_data['longitude'] = data['longitude']
        last_valid_data['altitude'] = data['altitude']
        last_valid_data['satellites'] = data['satellites']
        last_valid_data['valid'] = True
    if data['pressure'] != 0:
        last_valid_data['pressure'] = data['pressure']

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

    sys.stdout.write("Waiting for data packets...\n")

    while True:
        try:
            packet = rfm9x.receive(timeout=5.0)
            if packet is not None:
                data = decode_data(packet)
                if data:
                    # If valid GPS data, update and use new data
                    if data['satellites'] > 0 and data['satellites'] < 100:
                        update_valid_data(data)
                        q = data['quaternions']
                        sys.stdout.write(f"{q[0]},{q[1]},{q[2]},{q[3]},{data['longitude']},{data['latitude']},{data['altitude']},{data['satellites']},{data['pressure']},{rfm9x.last_rssi}\n")
                    # If invalid GPS data, use last valid data for GPS fields
                    else:
                        q = data['quaternions']
                        sys.stdout.write(f"{q[0]},{q[1]},{q[2]},{q[3]},{last_valid_data['longitude']},{last_valid_data['latitude']},{last_valid_data['altitude']},{last_valid_data['satellites']},{data['pressure']},{rfm9x.last_rssi}\n")
            time.sleep(0.1)
        except Exception as e:
            sys.stdout.write(f"Reception error: {e}\n")
            time.sleep(1)

except Exception as e:
    sys.stdout.write(f"Initialization error: {e}\n")

