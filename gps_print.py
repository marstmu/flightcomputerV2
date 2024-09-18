from machine import UART, Pin
import time

# Initialize UART (TX on GPIO 0, RX on GPIO 1)
uart = UART(1, baudrate=9600, tx=Pin(0), rx=Pin(1))

# Function to read and decode NMEA sentences
def read_gps():
    if uart.any():
        sentence = uart.readline().decode('utf-8', errors='ignore').strip()
        if sentence.startswith('$GPGGA'):
            parse_gpgga(sentence)
        elif sentence.startswith('$GPRMC'):
            parse_gprmc(sentence)

# Parse the GPGGA sentence (gps fix data)
def parse_gpgga(sentence):
    try:
        parts = sentence.split(',')
        if parts[6] == '0':
            print("No fix available")
            return

        latitude = convert_to_degrees(parts[2], parts[3])
        longitude = convert_to_degrees(parts[4], parts[5])
        altitude = parts[9]

        print("GPGGA Sentence:")
        print("Latitude: {}".format(latitude))
        print("Longitude: {}".format(longitude))
        print("Altitude: {} meters".format(altitude))
    except Exception as e:
        print("Error parsing GPGGA:", e)

# Parse the GPRMC sentence (recommended minimum navigation information)
def parse_gprmc(sentence):
    try:
        parts = sentence.split(',')
        if parts[2] == 'V':  # 'V' means data invalid
            print("No valid position data")
            return

        latitude = convert_to_degrees(parts[3], parts[4])
        longitude = convert_to_degrees(parts[5], parts[6])
        speed = parts[7]
        date = parts[9]

        print("GPRMC Sentence:")
        print("Latitude: {}".format(latitude))
        print("Longitude: {}".format(longitude))
        print("Speed: {} knots".format(speed))
        print("Date: {}".format(date))
    except Exception as e:
        print("Error parsing GPRMC:", e)

# Convert NMEA latitude/longitude to degrees
def convert_to_degrees(value, direction):
    if value == '':
        return None

    degrees = int(value[:2])
    minutes = float(value[2:])
    decimal_degrees = degrees + (minutes / 60)

    if direction == 'S' or direction == 'W':
        decimal_degrees = -decimal_degrees

    return decimal_degrees

# Main loop to continuously read GPS data
def main():
    while True:
        read_gps()
        time.sleep(1)

main()
