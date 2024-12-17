from micropython_rfm9x import *
from machine import SPI, Pin
import struct
import time

def decode_quaternions(data):
    try:
        if len(data) != 16:  # 4 floats * 4 bytes each
            raise ValueError("Invalid data length")
        return struct.unpack('ffff', data)
    except Exception as e:
        print(f"Decoding error: {e}")
        return None

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
    
    print("Waiting for quaternion packets...")
    
    while True:
        try:
            packet = rfm9x.receive(timeout=5.0)
            if packet is not None:
                quaternions = decode_quaternions(packet)
                if quaternions:
                    print("Received quaternions:", quaternions)
                    print(f"RSSI: {rfm9x.last_rssi} dB")
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Reception error: {e}")
            time.sleep(1)
            
except Exception as e:
    print(f"Initialization error: {e}")
