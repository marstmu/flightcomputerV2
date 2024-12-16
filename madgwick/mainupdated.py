import time
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data, read_temp, set_accel_scale, set_gyro_scale
from fusionmadgwickold import Fusion
import sys

# Initialize Fusion object
fuse = Fusion()

def main():
    if read_who_am_i() == 0x67:
        print("ICM-42670-P detected.")
        configure_sensor()

        # Set accelerometer and gyroscope scales
        set_accel_scale(3)  # ±16g
        set_gyro_scale(1)   # ±500 dps

        while True:
            # Read sensor data
            accel = read_accel_data()
            gyro = read_gyro_data()
            
            # Update fusion with new sensor data
            fuse.update_nomag(accel, gyro)
            
            # Get quaternions
            q1, q2, q3, q4 = fuse.q
            
            # Output quaternions to serial port
            sys.stdout.write(f"{q1:.6f},{q2:.6f},{q3:.6f},{q4:.6f}\n")
            
            # Optional: Print raw sensor data for debugging
            # print("Accel: X={:5.2f} g, Y={:5.2f} g, Z={:5.2f} g".format(accel[0], accel[1], accel[2]))
            # print("Gyro: X={:7.2f} deg/s, Y={:7.2f} deg/s, Z={:7.2f} deg/s".format(gyro[0], gyro[1], gyro[2]))
            
            time.sleep(0.01)  # 10ms delay for stable readings
    else:
        print("ICM-42670-P not found.")

if __name__ == "__main__":
    main()

