from machine import SPI, Pin
import time

spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))

def check_device():
    response = spi.read(1, 0x00)
    if response and response[0] != 0xFF:
        print("device detected:", response)
        return True
    else:
        print("no response from device")
        return False

while True:
    device_present = check_device()
    if device_present:
        print("device is present")
    else:
        print("no device detected")
    time.sleep(1)
