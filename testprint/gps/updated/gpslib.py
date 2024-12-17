from machine import UART, Pin
import time

class L86GPS:
    def __init__(self, uart_id=1, tx_pin=0, rx_pin=1):
        # Default baudrate is 9600 according to datasheet
        self.uart = UART(uart_id, baudrate=9600, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.init_module()
    
    def init_module(self):
        # Enable default configurations as per datasheet
        self._send_command("$PMTK286,1*23")  # Enable AIC
        self._send_command("$PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0*28")  # Enable default NMEA sentences
        self._send_command("$PMTK220,1000*1F")  # Set update rate to 1Hz
        
    def _send_command(self, command):
        self.uart.write((command + '\r\n').encode())
        time.sleep(0.1)
    
    def read_gps(self):
        if self.uart.any():
            try:
                sentence = self.uart.readline().decode('utf-8').strip()
                if sentence.startswith('$GPGGA'):
                    return self.parse_gpgga(sentence)
                elif sentence.startswith('$GPRMC'):
                    return self.parse_gprmc(sentence)
                elif sentence.startswith('$GPTXT'):
                    return self.parse_gptxt(sentence)
            except Exception:
                return None
        return None
    
    def parse_gpgga(self, sentence):
        try:
            parts = sentence.split(',')
            if parts[6] == '0':  # Fix quality indicator
                return {'type': 'GPGGA', 'status': 'no_fix'}
            
            return {
                'type': 'GPGGA',
                'status': 'valid',
                'time': parts[1],
                'latitude': self._convert_to_degrees(parts[2], parts[3]),
                'longitude': self._convert_to_degrees(parts[4], parts[5]),
                'quality': int(parts[6]),
                'satellites': int(parts[7]),
                'altitude': float(parts[9]),
                'altitude_unit': parts[10]
            }
        except Exception as e:
            return {'type': 'GPGGA', 'status': 'error', 'error': str(e)}
    
    def parse_gprmc(self, sentence):
        try:
            parts = sentence.split(',')
            if parts[2] != 'A':  # A = valid, V = invalid
                return {'type': 'GPRMC', 'status': 'invalid'}
            
            return {
                'type': 'GPRMC',
                'status': 'valid',
                'time': parts[1],
                'latitude': self._convert_to_degrees(parts[3], parts[4]),
                'longitude': self._convert_to_degrees(parts[5], parts[6]),
                'speed': float(parts[7]),
                'date': parts[9]
            }
        except Exception as e:
            return {'type': 'GPRMC', 'status': 'error', 'error': str(e)}
    
    def parse_gptxt(self, sentence):
        # Parse antenna status messages
        try:
            parts = sentence.split(',')
            if 'ANTSTATUS' in sentence:
                return {
                    'type': 'GPTXT',
                    'antenna_status': parts[-1].split('*')[0]
                }
        except Exception:
            return None
    
    def _convert_to_degrees(self, value, direction):
        if not value:
            return None
        
        try:
            # Handle NMEA format (ddmm.mmmm)
            decimal_degrees = float(value[:2]) + float(value[2:]) / 60.0
            if direction in ['S', 'W']:
                decimal_degrees = -decimal_degrees
            return round(decimal_degrees, 6)
        except Exception:
            return None
            
    def enable_easy(self):
        self._send_command("$PMTK869,1,1*34")
        
    def disable_easy(self):
        self._send_command("$PMTK869,1,0*34")
        
    def enter_standby(self):
        self._send_command("$PMTK161,0*28")
        
    def enter_backup(self):
        self._send_command("$PMTK225,4*2F")
