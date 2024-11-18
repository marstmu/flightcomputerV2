from machine import I2C, Pin
import time

# I2C address
LPS22H_I2C_ADDRESS = 0x5C

# LPS22H registers
LPS22H_WHO_AM_I = 0x0F
LPS22H_CTRL_REG1 = 0x10
LPS22H_PRESS_OUT_XL = 0x28
LPS22H_TEMP_OUT_L = 0x2B

# Initialize I2C (SCL on GPIO 9, SDA on GPIO 8)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

def write_register(reg, data):
    i2c.writeto_mem(LPS22H_I2C_ADDRESS, reg, bytes([data]))

def read_register(reg, num_bytes=1):
    return i2c.readfrom_mem(LPS22H_I2C_ADDRESS, reg, num_bytes)

def read_who_am_i():
    who_am_i = read_register(LPS22H_WHO_AM_I)
    return who_am_i[0]

def configure_lps22h():
    # Setup the sensor with default configuration (ODR 10 Hz, enable block data update)
    write_register(LPS22H_CTRL_REG1, 0x50)

def read_pressure():
    # LPS22H gives pressure in 3 bytes (XLSB, LSB, MSB)
    press_raw = read_register(LPS22H_PRESS_OUT_XL, 3)
    press_raw_val = press_raw[2] << 16 | press_raw[1] << 8 | press_raw[0]
    
    # Convert to kPa
    pressure_kpa = press_raw_val / 409.6
    return pressure_kpa

def read_temperature():
    # LPS22H gives temperature in 2 bytes (LSB, MSB)
    temp_raw = read_register(LPS22H_TEMP_OUT_L, 2)
    temp_raw_val = temp_raw[1] << 8 | temp_raw[0]
    
    # Convert to C
    temperature_c = temp_raw_val / 100.0
    return temperature_c

# Main loop to read pressure and temperature
def main():
    if read_who_am_i() == 0xB1:  # Check if LPS22H is responding
        print("LPS22H detected.")
        configure_lps22h()
        
        while True:
            pressure = read_pressure()
            temperature = read_temperature()
            
            print("Pressure: {:.2f} kPa, Temperature: {:.2f} °C".format(pressure, temperature))
            time.sleep(1)
    else:
        print("LPS22H not found.")

main()
