from l86gps import L86GPS
import time

def main():
    # Initialize GPS module with default pins (UART1, TX=0, RX=1)
    gps = L86GPS()
    
    print("GPS Module initialized. Waiting for data...")
    
    while True:
        # Read GPS data
        data = gps.read_gps()
        
        if data:
            # Process GPGGA sentences (position data)
            if data['type'] == 'GPGGA':
                if data['status'] == 'valid':
                    print("\nGPS Position:")
                    print(f"Time: {data['time']}")
                    print(f"Latitude: {data['latitude']}°")
                    print(f"Longitude: {data['longitude']}°")
                    print(f"Altitude: {data['altitude']} {data['altitude_unit']}")
                    print(f"Satellites: {data['satellites']}")
                    print(f"Fix Quality: {data['quality']}")
                elif data['status'] == 'no_fix':
                    print("Waiting for GPS fix...")
            
            # Process GPRMC sentences (speed and date)
            elif data['type'] == 'GPRMC':
                if data['status'] == 'valid':
                    print("\nGPS Movement:")
                    print(f"Speed: {data['speed']} knots")
                    print(f"Date: {data['date']}")
            
            # Process antenna status messages
            elif data['type'] == 'GPTXT':
                print(f"\nAntenna Status: {data['antenna_status']}")
        
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
