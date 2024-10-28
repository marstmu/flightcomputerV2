from machine import I2C, Pin
import time
from kalmanfilter import KalmanFilter
import sys

# ICM-42670-P I2C address and registers
ICM42670_I2C_ADDRESS = 0x69
ICM42670_WHO_AM_I = 0x75
ICM42670_PWR_MGMT_1 = 0x1F

# Initialize I2C (SCL on GPIO 9, SDA on GPIO 8)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

# Functions to communicate with the sensor
def write_register(reg, data):
    i2c.writeto_mem(ICM42670_I2C_ADDRESS, reg, bytes([data]))

def read_register_int(reg, num_bytes=1):
    return int.from_bytes(i2c.readfrom_mem(ICM42670_I2C_ADDRESS, reg, num_bytes), "little")

def configure_sensor():
    write_register(ICM42670_PWR_MGMT_1, 0b10001111)

def read_accel_data():
    raw_accel_x = (read_register_int(0x0B) << 8 | read_register_int(0x0C))
    raw_accel_y = (read_register_int(0x0D) << 8 | read_register_int(0x0E))
    raw_accel_z = (read_register_int(0x0F) << 8 | read_register_int(0x10))
    raw_accel_x = raw_accel_x - 65536 if raw_accel_x > 32767 else raw_accel_x
    raw_accel_y = raw_accel_y - 65536 if raw_accel_y > 32767 else raw_accel_y
    raw_accel_z = raw_accel_z - 65536 if raw_accel_z > 32767 else raw_accel_z
    return (raw_accel_x / 2129.92, raw_accel_y / 2129.92, raw_accel_z / 2129.92)

def read_gyro_data():
    raw_gyro_x = (read_register_int(0x11) << 8 | read_register_int(0x12))
    raw_gyro_y = (read_register_int(0x13) << 8 | read_register_int(0x14))
    raw_gyro_z = (read_register_int(0x15) << 8 | read_register_int(0x16))
    raw_gyro_x = raw_gyro_x - 65536 if raw_gyro_x > 32767 else raw_gyro_x
    raw_gyro_y = raw_gyro_y - 65536 if raw_gyro_y > 32767 else raw_gyro_y
    raw_gyro_z = raw_gyro_z - 65536 if raw_gyro_z > 32767 else raw_gyro_z
    return (raw_gyro_x / 131, raw_gyro_y / 131, raw_gyro_z / 131)

# Initialize Kalman filters for each axis
dt = 0.01  # Time step in seconds
process_noise = 0.01
measurement_noise = 1.0
kf_x = KalmanFilter(dt, process_noise, measurement_noise)  # Pitch (X)
kf_y = KalmanFilter(dt, process_noise, measurement_noise)  # Roll (Y)
kf_z = KalmanFilter(dt, process_noise, measurement_noise)  # Yaw (Z)

def main():
    if read_register_int(ICM42670_WHO_AM_I) == 0x67:
        print("ICM-42670-P detected.")
        configure_sensor()
        
        while True:
            accel = read_accel_data()
            gyro = read_gyro_data()
            
            # Predict step for each axis
            kf_x.predict()
            kf_y.predict()
            kf_z.predict()

            # Update step for each axis using respective accelerometer data
            kf_x.update([[accel[0]]])  # X-axis (pitch)
            kf_y.update([[accel[1]]])  # Y-axis (roll)
            kf_z.update([[gyro[2]]])   # Z-axis (yaw) uses gyro only since accel doesn't capture rotation around z-axis
            
            # Get estimated angles from each Kalman filter
            estimated_pitch = kf_x.get_state()[0][0]
            estimated_roll = kf_y.get_state()[0][0]
            estimated_yaw = kf_z.get_state()[0][0]

            # Print the estimated angles
            print(f"Pitch: {estimated_pitch:.6f}, Roll: {estimated_roll:.6f}, Yaw: {estimated_yaw:.6f}")
            time.sleep(dt)  # Wait for the next loop
    else:
        print("ICM-42670-P not found.")

# Run the main loop
main()

