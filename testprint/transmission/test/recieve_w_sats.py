# receiver.py
from micropython_rfm9x import *
from machine import SPI, Pin
import struct
import time

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
        print(f"Decoding error: {e}")
        return None

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

    print("Waiting for data packets...")

    while True:
        try:
            packet = rfm9x.receive(timeout=5.0)
            if packet is not None:
                data = decode_data(packet)
                if data:
                    print("\nReceived Data:")
                    print(f"Quaternions: {data['quaternions']}")
                    print(f"GPS: {data['latitude']}°, {data['longitude']}°")
                    print(f"Altitude: {data['altitude']} m")
                    print(f"Satellites: {data['satellites']}")
                    print(f"Pressure: {data['pressure']} hPa")
                    print(f"RSSI: {rfm9x.last_rssi} dB")
            time.sleep(0.1)
        except Exception as e:
            print(f"Reception error: {e}")
            time.sleep(1)

except Exception as e:
    print(f"Initialization error: {e}")

