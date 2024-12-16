from micropython_rfm9x import *
from machine import SPI, Pin
import time

# Pin Configuration
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
    miso=Pin(16)
)

RADIO_FREQ_MHZ = 915.0

# Initialize RFM radio with error handling
try:
    rfm9x = RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
    rfm9x.tx_power = 14
    
    # Configure for better reliability
    rfm9x.signal_bandwidth = 125000
    rfm9x.coding_rate = 5
    rfm9x.spreading_factor = 7
    rfm9x.enable_crc = True
    
    while True:
        try:
            message = bytes("Hello world!\r\n", "utf-8")
            rfm9x.send(message)
            print("Sent Hello World message!")
            print(f"Signal strength: {rfm9x.last_rssi} dB")
            time.sleep(2)  # Add delay between transmissions
            
        except Exception as e:
            print(f"Transmission error: {e}")
            time.sleep(1)
            
except Exception as e:
    print(f"Initialization error: {e}")
