# icm42670.py

from machine import I2C, Pin
import math

# ICM-42670-P I2C address
ICM42670_I2C_ADDRESS = 0x69

# ICM-42670-P Registers
ICM42670_WHO_AM_I = 0x75
ICM42670_PWR_MGMT_1 = 0x1F
ICM42670_ACCEL_CONFIG = 0x1C
ICM42670_GYRO_CONFIG = 0x1B

# Constants for unit conversion
G_TO_MS2 = 9.81
DEG_TO_RAD = math.pi / 180

# Initialize I2C (SCL on GPIO 9, SDA on GPIO 8)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

def write_register(reg, data):
    i2c.writeto_mem(ICM42670_I2C_ADDRESS, reg, bytes([data]))

def read_register(reg, num_bytes=1):
    return i2c.readfrom_mem(ICM42670_I2C_ADDRESS, reg, num_bytes)

def read_register_int(reg, num_bytes=1):
    return int.from_bytes(i2c.readfrom_mem(ICM42670_I2C_ADDRESS, reg, num_bytes), "little")

def read_who_am_i():
    who_am_i = read_register(ICM42670_WHO_AM_I)
    return who_am_i[0]

def configure_sensor():
    write_register(ICM42670_PWR_MGMT_1, 0b10001111)

def set_accel_scale(scale):
    if scale not in [0, 1, 2, 3]:
        raise ValueError("Invalid accelerometer scale")
    write_register(ICM42670_ACCEL_CONFIG, scale)

def set_gyro_scale(scale):
    if scale not in [0, 1, 2, 3]:
        raise ValueError("Invalid gyroscope scale")
    write_register(ICM42670_GYRO_CONFIG, scale)

def read_temp():
    return (read_register_int(0x09) << 8 | read_register_int(0x0A))

def read_accel_data():
    accel_x = (read_register_int(0x0B) << 8 | read_register_int(0x0C))
    accel_y = (read_register_int(0x0D) << 8 | read_register_int(0x0E))
    accel_z = (read_register_int(0x0F) << 8 | read_register_int(0x10))

    accel_x = accel_x - 65536 if accel_x > 32767 else accel_x
    accel_y = accel_y - 65536 if accel_y > 32767 else accel_y
    accel_z = accel_z - 65536 if accel_z > 32767 else accel_z

    scale = read_register(ICM42670_ACCEL_CONFIG)[0] & 0x03
    scale_factors = [2048.0, 1024.0, 512.0, 256.0]
    scale_factor = scale_factors[scale]

    accel_x_ms2 = (accel_x / scale_factor) * G_TO_MS2
    accel_y_ms2 = (accel_y / scale_factor) * G_TO_MS2
    accel_z_ms2 = (accel_z / scale_factor) * G_TO_MS2

    return (accel_x_ms2, accel_y_ms2, accel_z_ms2)

def read_gyro_data():
    gyro_x = (read_register_int(0x11) << 8 | read_register_int(0x12))
    gyro_y = (read_register_int(0x13) << 8 | read_register_int(0x14))
    gyro_z = (read_register_int(0x15) << 8 | read_register_int(0x16))

    gyro_x = gyro_x - 65536 if gyro_x > 32767 else gyro_x
    gyro_y = gyro_y - 65536 if gyro_y > 32767 else gyro_y
    gyro_z = gyro_z - 65536 if gyro_z > 32767 else gyro_z

    scale = read_register(ICM42670_GYRO_CONFIG)[0] & 0x03
    scale_factors = [131.0, 65.5, 32.8, 16.4]
    scale_factor = scale_factors[scale]

    gyro_x_rad_s = (gyro_x / scale_factor) * DEG_TO_RAD
    gyro_y_rad_s = (gyro_y / scale_factor) * DEG_TO_RAD
    gyro_z_rad_s = (gyro_z / scale_factor) * DEG_TO_RAD

    return (gyro_x_rad_s, gyro_y_rad_s, gyro_z_rad_s)
