import machine
import time

i2c = machine.I2C(0, scl=machine.Pin(9), sda=machine.Pin(8))

def scan_i2c():
    devices = i2c.scan()
    return devices

def main():
    print("scanning i2c")
    devices = scan_i2c()
    if devices:
        print(f"found {len(devices)} device(s) at addresses: {', '.join([hex(dev) for dev in devices])}")
    else:
        print("no devices found")

main()

