from machine import Pin, I2C
import neopixel
import time
import _thread

# LED setup
p = 2
n = 1
np = neopixel.NeoPixel(Pin(p), n)

def wheel(pos, intensity=0.5):
    # Generate rainbow colors across 0-255 positions with reduced intensity.
    if pos < 85:
        return (int(pos * 3 * intensity), int((255 - pos * 3) * intensity), int(0 * intensity))
    elif pos < 170:
        pos -= 85
        return (int((255 - pos * 3) * intensity), int(0 * intensity), int(pos * 3 * intensity))
    else:
        pos -= 170
        return (int(0 * intensity), int(pos * 3 * intensity), int((255 - pos * 3) * intensity))

def neopixel_task():
    while True:
        for i in range(256):
            np[0] = wheel(i, intensity=0.05)  # Adjust the intensity here
            np.write()
            time.sleep(0.01)  # Adjust the speed of the color cycle

# ICM-42670-P setup
ICM42670_I2C_ADDRESS = 0x69
ICM42670_WHO_AM_I = 0x75
ICM42670_PWR_MGMT_1 = 0x1F

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
    # Set the sensor to its normal operation mode
    write_register(ICM42670_PWR_MGMT_1, 0b10001111)
    
def read_temp():
    return (read_register_int(0x09) << 8 | read_register_int(0x0A))

def read_accel_data():
    # Convert to 16-bit integers (MSB << 8 | LSB)
    accel_x = (read_register_int(0x0B) << 8 | read_register_int(0x0C))
    accel_y = (read_register_int(0x0D) << 8 | read_register_int(0x0E))
    accel_z = (read_register_int(0x0F) << 8 | read_register_int(0x10))

    # Adjust for two's complement (if negative)
    accel_x = accel_x - 65536 if accel_x > 32767 else accel_x
    accel_y = accel_y - 65536 if accel_y > 32767 else accel_y
    accel_z = accel_z - 65536 if accel_z > 32767 else accel_z

    # Convert raw values into g's
    accel_x_g = accel_x / 2129.92
    accel_y_g = accel_y / 2129.92
    accel_z_g = accel_z / 2129.92

    return (accel_x_g, accel_y_g, accel_z_g)

def read_gyro_data():  
    # Convert to 16-bit integers (MSB << 8 | LSB)
    gyro_x = (read_register_int(0x11) << 8 | read_register_int(0x12))
    gyro_y = (read_register_int(0x13) << 8 | read_register_int(0x14))
    gyro_z = (read_register_int(0x15) << 8 | read_register_int(0x16))

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
        configure_sensor()
        
        while True:
            accel = read_accel_data()
            gyro = read_gyro_data()
            
            print("Accel: X={:7.2f} g, Y={:7.2f} g, Z={:7.2f} g".format(accel[0], accel[1], accel[2]))
            print("Gyro: X={:7.2f}°/s, Y={:7.2f}°/s, Z={:7.2f}°/s".format(gyro[0], gyro[1], gyro[2]))
            print("Temp: {:4.2f}".format((read_temp() / 128) + 25))            
            time.sleep(0.05)
    else:
        print("ICM-42670-P not found.")

# Start the NeoPixel task on the second core
_thread.start_new_thread(neopixel_task, ())

# Run the main loop on the first core
main()
w
