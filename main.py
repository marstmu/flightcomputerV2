from machine import I2C, Pin
import time
from fusionmadgwick import Fusion  # Import Fusion library
import sys

# ICM-42670-P I2C address and registers
ICM42670_I2C_ADDRESS = 0x69
ICM42670_WHO_AM_I = 0x75
ICM42670_PWR_MGMT_1 = 0x1F

# Initialize I2C (SCL on GPIO 9, SDA on GPIO 8)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

# Initialize Fusion object
fuse = Fusion()

def write_register(reg, data):
    i2c.writeto_mem(ICM42670_I2C_ADDRESS, reg, bytes([data]))

def read_register_int(reg, num_bytes=1):
    return int.from_bytes(i2c.readfrom_mem(ICM42670_I2C_ADDRESS, reg, num_bytes), "little")

def read_who_am_i():
    who_am_i = i2c.readfrom_mem(ICM42670_I2C_ADDRESS, ICM42670_WHO_AM_I, 1)
    return who_am_i[0]

def configure_sensor():
    write_register(ICM42670_PWR_MGMT_1, 0b10001111)

def read_accel_data():
    # Read raw accelerometer data (X, Y, Z)
    raw_accel_x = (read_register_int(0x0B) << 8 | read_register_int(0x0C))
    raw_accel_y = (read_register_int(0x0D) << 8 | read_register_int(0x0E))
    raw_accel_z = (read_register_int(0x0F) << 8 | read_register_int(0x10))
    # Adjust for signed integers
    raw_accel_x = raw_accel_x - 65536 if raw_accel_x > 32767 else raw_accel_x
    raw_accel_y = raw_accel_y - 65536 if raw_accel_y > 32767 else raw_accel_y
    raw_accel_z = raw_accel_z - 65536 if raw_accel_z > 32767 else raw_accel_z
    # Convert raw data to acceleration in g's
    accel_x_g = raw_accel_x / 2129.92
    accel_y_g = raw_accel_y / 2129.92
    accel_z_g = raw_accel_z / 2129.92
    return (accel_x_g, accel_y_g, accel_z_g)

def read_gyro_data():
    # Read raw gyroscope data (X, Y, Z)
    raw_gyro_x = (read_register_int(0x11) << 8 | read_register_int(0x12))
    raw_gyro_y = (read_register_int(0x13) << 8 | read_register_int(0x14))
    raw_gyro_z = (read_register_int(0x15) << 8 | read_register_int(0x16))
    # Adjust for signed integers
    raw_gyro_x = raw_gyro_x - 65536 if raw_gyro_x > 32767 else raw_gyro_x
    raw_gyro_y = raw_gyro_y - 65536 if raw_gyro_y > 32767 else raw_gyro_y
    raw_gyro_z = raw_gyro_z - 65536 if raw_gyro_z > 32767 else raw_gyro_z
    # Convert raw data to angular velocity in dps
    gyro_x_dps = raw_gyro_x / 12 #131.0
    gyro_y_dps = raw_gyro_y / 12 #131.0
    gyro_z_dps = raw_gyro_z / 12 #131.0
    return (gyro_x_dps, gyro_y_dps, gyro_z_dps)

# Main loop with sensor fusion integration
def main():
    if read_who_am_i() == 0x67:  # Check if ICM-42670-P is responding
        print("ICM-42670-P detected.")
        configure_sensor()
        while True:
            accel = read_accel_data()  # Read and print raw accelerometer data
            gyro = read_gyro_data()    # Read and print raw gyroscope data
            
            # Use Fusion library for sensor fusion
            fuse.update_nomag(accel, gyro)  # Update using accelerometer and gyroscope data
            
            # Get quaternions
            q1, q2, q3, q4 = fuse.q

            # Output the quaternions to the serial port
            sys.stdout.write(f"{q1:.6f},{q2:.6f},{q3:.6f},{q4:.6f}\n")
            time.sleep(0.01)  # Delay for 10ms
    else:
        print("ICM-42670-P not found.")

# Run the main loop
main()


