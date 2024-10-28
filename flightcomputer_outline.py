import machine
import utime
import ustruct
from machine import Pin, I2C, SPI, UART
from flashbdev import bdev  # make sure theres a proper library for flash access
from LPS22H import LPS22H  # Pressure sensor library
from Adafruit_GPS import GPS  # GPS library
from LoRa import LoRa  # LoRa library
from IMU import IMU  # IMU library

# config
FLASH_SECTOR_SIZE = 4096  # sector size
ACCELERATION_THRESHOLD = 9.81  # 1g

# initialize peripherals
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
gps_uart = UART(1, baudrate=9600, tx=Pin(0), rx=Pin(1))
spi = SPI(0, baudrate=1000000, polarity=0, phase=0)  # Adjust settings as needed
lora = LoRa(spi, ) # fix spi
imu = IMU(i2c)

flash = bdev  # Replace flash access method
pressure_sensor = LPS22H(i2c)
gps = GPS(gps_uart)

def read_imu_data():
    # placeholder for reading IMU data
    return imu.read_acceleration()

def read_pressure():
    # placeholder for reading pressure sensor data
    return pressure_sensor.read_pressure()

def read_gps():
    # placeholder for reading GPS data
    gps.update()
    if gps.has_fix():
        return gps.latitude, gps.longitude
    return None

def write_data_to_flash(data, address):
    # write data to flash memory at the specified address
    flash.write(address, data)

def log_data():
    # check for rocket launch
    acceleration = read_imu_data()
    if acceleration > ACCELERATION_THRESHOLD:
        # high speed logging mode
        write_data_interval = 100  # high speed interval in ms
    else:
        # low speed logging mode
        write_data_interval = 1000  # low speed interval in ms

    last_write_time = utime.ticks_ms()
    address = 0

    while True:
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_write_time) > write_data_interval:
            # collect data
            pressure = read_pressure()
            gps_data = read_gps()
            imu_data = read_imu_data()

            # format data
            data = ustruct.pack('fff', pressure, imu_data[0], imu_data[1], imu_data[2])
            if gps_data:
                data += ustruct.pack('ff', gps_data[0], gps_data[1])

            # write data to flash
            write_data_to_flash(data, address)
            address += len(data)
            if address > FLASH_SECTOR_SIZE:
                address = 0  # loop back to beginning of flash

            # update last write time
            last_write_time = current_time

def send_data():
    while True:
        # collect data
        pressure = read_pressure()
        gps_data = read_gps()
        imu_data = read_imu_data()

        # format data
        data = ustruct.pack('fff', pressure, imu_data[0], imu_data[1], imu_data[2])
        if gps_data:
            data += ustruct.pack('ff', gps_data[0], gps_data[1])

        # send data via LoRa
        lora.send(data)

        utime.sleep(10)  # send data every ten seconds

def main():
    # start tasks
    utime.sleep(5)  # delay for initialization
    log_data_thread = machine.Thread(target=log_data)
    send_data_thread = machine.Thread(target=send_data)

    log_data_thread.start()
    send_data_thread.start()

if __name__ == '__main__':
    main()
