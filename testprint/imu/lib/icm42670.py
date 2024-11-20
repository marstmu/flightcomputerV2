# icm42670.py

from machine import I2C, Pin

# ICM-42670-P I2C address
ICM42670_I2C_ADDRESS = 0x69  

# ICM-42670-P Registers
ICM42670_WHO_AM_I = 0x75
ICM42670_PWR_MGMT_1 = 0x1F
ICM42670_ACCEL_CONFIG = 0x1C    # Accelerometer configuration register
ICM42670_GYRO_CONFIG = 0x1B    # Gyroscope configuration register

# Initialize I2C (SCL on GPIO 9, SDA on GPIO 8)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

def write_register(reg, data):
    """Write a byte of data to a register."""
    i2c.writeto_mem(ICM42670_I2C_ADDRESS, reg, bytes([data]))

def read_register(reg, num_bytes=1):
    """Read a number of bytes from a register."""
    return i2c.readfrom_mem(ICM42670_I2C_ADDRESS, reg, num_bytes)

def read_register_int(reg, num_bytes=1):
    """Read an integer from a register."""
    return int.from_bytes(i2c.readfrom_mem(ICM42670_I2C_ADDRESS, reg, num_bytes), "little")

def read_who_am_i():
    """Read the WHO_AM_I register to verify the sensor is present."""
    who_am_i = read_register(ICM42670_WHO_AM_I)
    return who_am_i[0]

def configure_sensor():
    """Configure the sensor for normal operation."""
    write_register(ICM42670_PWR_MGMT_1, 0b10001111)

def set_accel_scale(scale):
    """Set the accelerometer scale: 0=±2g, 1=±4g, 2=±8g, 3=±16g."""
    if scale not in [0, 1, 2, 3]:
        raise ValueError("Invalid accelerometer scale")
    
    write_register(ICM42670_ACCEL_CONFIG, scale)

def set_gyro_scale(scale):
    """Set the gyroscope scale: 0=±250 dps, 1=±500 dps, 2=±1000 dps, 3=±2000 dps."""
    if scale not in [0, 1, 2, 3]:
        raise ValueError("Invalid gyroscope scale")
    
    write_register(ICM42670_GYRO_CONFIG, scale)

def read_temp():
    """Read the temperature data."""
    return (read_register_int(0x09) << 8 | read_register_int(0x0A))

def read_accel_data():
    """Read the raw accelerometer data."""
    accel_x = (read_register_int(0x0B) << 8 | read_register_int(0x0C))
    accel_y = (read_register_int(0x0D) << 8 | read_register_int(0x0E))
    accel_z = (read_register_int(0x0F) << 8 | read_register_int(0x10))

    # Adjust for two's complement if necessary
    accel_x = accel_x - 65536 if accel_x > 32767 else accel_x
    accel_y = accel_y - 65536 if accel_y > 32767 else accel_y
    accel_z = accel_z - 65536 if accel_z > 32767 else accel_z

    return (accel_x, accel_y, accel_z)

def read_gyro_data():
    """Read the raw gyroscope data."""
    gyro_x = (read_register_int(0x11) << 8 | read_register_int(0x12))
    gyro_y = (read_register_int(0x13) << 8 | read_register_int(0x14))
    gyro_z = (read_register_int(0x15) << 8 | read_register_int(0x16))

    # Adjust for two's complement if necessary
    gyro_x = gyro_x - 65536 if gyro_x > 32767 else gyro_x
    gyro_y = gyro_y - 65536 if gyro_y > 32767 else gyro_y
    gyro_z = gyro_z - 65536 if gyro_z > 32767 else gyro_z

    return (gyro_x, gyro_y, gyro_z)
