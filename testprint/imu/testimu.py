import time
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data, read_temp, set_accel_scale, set_gyro_scale

def main():
    if read_who_am_i() == 0x67:
        print("ICM-42670-P detected.")
        configure_sensor()

        # Set accelerometer and gyroscope scales
        set_accel_scale(3)  # ±16g
        set_gyro_scale(3)   # ±2000 dps

        while True:
            accel = read_accel_data()
            gyro = read_gyro_data()
            
            print("Accel: X={:5.2f} m/s², Y={:5.2f} m/s², Z={:5.2f} m/s²".format(accel[0], accel[1], accel[2]))
            print("Gyro: X={:7.2f} rad/s, Y={:7.2f} rad/s, Z={:7.2f} rad/s".format(gyro[0], gyro[1], gyro[2]))
            print("Temp: {:4.2f}°C".format((read_temp() / 128) + 25))
            
            time.sleep(0.05)
    else:
        print("ICM-42670-P not found.")

if __name__ == "__main__":
    main()
