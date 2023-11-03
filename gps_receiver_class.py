import time

import serial
import pynmea2


class GPSReceiver:
    def __init__(self, port='/dev/ttyACM0', baud=9600):
        self.port = port
        self.baud = baud
        self.serialPort = serial.Serial(self.port, baudrate=self.baud, timeout=0.5)
    
    @staticmethod
    def _convert_to_decimal(degrees_minutes):
        """Converts a NMEA GPS value (degrees and minutes) to decimal degrees."""
        d, m = divmod(float(degrees_minutes), 100)
        return d + m/60

    def get_location(self):
        while True:
            try:
                data = self.serialPort.readline()
                data = data.decode('ascii', errors='ignore').strip()  # Decode using ASCII and ignore invalid characters

                if 'GGA' in data:
                    msg = pynmea2.parse(data)
                    lat = self._convert_to_decimal(msg.lat)
                    if msg.lat_dir == 'S':
                        lat = -lat
                    lon = self._convert_to_decimal(msg.lon)
                    if msg.lon_dir == 'W':
                        lon = -lon
                    return lat, lon
            except Exception as e:
                print(e)
                continue

            time.sleep(0.1)

if __name__ == "__main__":
    # Example of how to use the class
    gps = GPSReceiver()
    lat, lon = gps.get_location()
    print(f"Latitude: {lat:.5f}, Longitude: {lon:.5f}")