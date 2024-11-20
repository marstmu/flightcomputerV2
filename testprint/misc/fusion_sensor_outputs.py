import time
from machine import Pin, I2C
from lib.icm42670 import configure_sensor, read_accel_data, read_gyro_data, set_accel_scale, set_gyro_scale
from micropython_mmc5603 import mmc5603

i2c = I2C(0, sda=Pin(8), scl=Pin(9))
mmc = mmc5603.MMC5603(i2c)

configure_sensor()
set_accel_scale(0)
set_gyro_scale(0)

def main():
    while True:
        mag_x, mag_y, mag_z = mmc.magnetic
        accel = read_accel_data()
        gyro = read_gyro_data()

        print("Accel: X={:5.2f} m/s², Y={:5.2f} m/s², Z={:5.2f} m/s²".format(accel[0], accel[1], accel[2]))
        print("Gyro: X={:7.2f} rad/s, Y={:7.2f} rad/s, Z={:7.2f} rad/s".format(gyro[0], gyro[1], gyro[2]))
        print(f"Mag: X={mag_x:.2f} uT, Y={mag_y:.2f} uT, Z={mag_z:.2f} uT")
        print()
        time.sleep(0.10)

if __name__ == "__main__":
    main()

