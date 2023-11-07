import time

import pynmea2
import serial

from iec_mgt_typing import Session


class GPS:
    def __init__(self, session: Session, port: str='/dev/ttyACM0', baud: int=9600):
        # Store reference to session as attribute
        self.session = session

        # Print debug info
        print(f"[INFO]: GPS initialized")
        
        #########################
        return # Remove this later
        #########################
        self.port = port
        self.baud = baud
        self.serialPort = serial.Serial(self.port, baudrate=self.baud, timeout=0.5)
        return


    @staticmethod
    def _convert_to_decimal(degrees_minutes):
        """Converts a NMEA GPS value (degrees and minutes) to decimal degrees."""
        d, m = divmod(float(degrees_minutes), 100)
        return d + m/60


    def run_one_iteration(self) -> None:
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

            # Assign values to shared geolocation attributes
            self.session.latitude.value = lat
            self.session.longitude.value = lon
            self.session.timestamp.value = time.time()
            return

        # Otherwise, raise an exception
        raise ValueError("No GPS data found")


    def get_location(self) -> None:
        while True:
            try:
                ######REMOVE THIS BLOCK LATER####
                lat, lon = 55.75, 37.61
                self.session.latitude.value = lat
                self.session.longitude.value = lon
                self.session.timestamp.value = time.time()
                ##################################
                # self.run_one_iteration() # Uncomment this later
                time.sleep(1)
            except Exception:
                pass
            time.sleep(0.1)
        return


    def run(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)


    def __call__(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)
