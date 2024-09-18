from machine import I2C, Pin
import time

# ICM-42670-P I2C address
ICM42670_I2C_ADDRESS = 0x68

# ICM-42670-P Registers
ICM42670_WHO_AM_I = 0x75
ICM42670_PWR_MGMT_1 = 0x4E
ICM42670_ACCEL_XOUT_H = 0x1F
ICM42670_GYRO_XOUT_H = 0x25

# Initialize I2C (SCL on GPIO 9, SDA on GPIO 8)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

def write_register(reg, data):
    i2c.writeto_mem(ICM42670_I2C_ADDRESS, reg, bytes([data]))

def read_register(reg, num_bytes=1):
    return i2c.readfrom_mem(ICM42670_I2C_ADDRESS, reg, num_bytes)

def read_who_am_i():
    who_am_i = read_register(ICM42670_WHO_AM_I)
    return who_am_i[0]

def configure_icm42670():
    # Set the sensor to its normal operation mode
    write_register(ICM42670_PWR_MGMT_1, 0x00)

def read_accel_data():
    accel_data = read_register(ICM42670_ACCEL_XOUT_H, 6)
    
    # Convert to 16-bit integers (MSB << 8 | LSB)
    accel_x = (accel_data[0] << 8 | accel_data[1])
    accel_y = (accel_data[2] << 8 | accel_data[3])
    accel_z = (accel_data[4] << 8 | accel_data[5])

    # Adjust for two's complement (if negative)
    accel_x = accel_x - 65536 if accel_x > 32767 else accel_x
    accel_y = accel_y - 65536 if accel_y > 32767 else accel_y
    accel_z = accel_z - 65536 if accel_z > 32767 else accel_z

    # Convert raw values to g's (using ±2g scale, 16384 LSB/g)
    accel_x_g = accel_x / 16384.0
    accel_y_g = accel_y / 16384.0
    accel_z_g = accel_z / 16384.0

    return (accel_x_g, accel_y_g, accel_z_g)

def read_gyro_data():
    gyro_data = read_register(ICM42670_GYRO_XOUT_H, 6)
    
    # Convert to 16-bit integers (MSB << 8 | LSB)
    gyro_x = (gyro_data[0] << 8 | gyro_data[1])
    gyro_y = (gyro_data[2] << 8 | gyro_data[3])
    gyro_z = (gyro_data[4] << 8 | gyro_data[5])

    # Adjust for two's complement (if negative)
    gyro_x = gyro_x - 65536 if gyro_x > 32767 else gyro_x
    gyro_y = gyro_y - 65536 if gyro_y > 32767 else gyro_y
    gyro_z = gyro_z - 65536 if gyro_z > 32767 else gyro_z

    # Convert raw values to degrees per second (using ±250 dps scale, 131 LSB/dps)
    gyro_x_dps = gyro_x / 131.0
    gyro_y_dps = gyro_y / 131.0
    gyro_z_dps = gyro_z / 131.0

    return (gyro_x_dps, gyro_y_dps, gyro_z_dps)

# Main loop to read accelerometer and gyroscope data
def main():
    if read_who_am_i() == 0x67:  # Check if ICM-42670-P is responding
        print("ICM-42670-P detected.")
        configure_icm42670()
        
        while True:
            accel = read_accel_data()
            gyro = read_gyro_data()
            
            print("Accel: X={:.2f}g, Y={:.2f}g, Z={:.2f}g".format(accel[0], accel[1], accel[2]))
            print("Gyro: X={:.2f}°/s, Y={:.2f}°/s, Z={:.2f}°/s".format(gyro[0], gyro[1], gyro[2]))
            
            time.sleep(1)
    else:
        print("ICM-42670-P not found.")

# Run the main loop
main()
