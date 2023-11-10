import time

import os
import gpsd

from iec_mgt_typing import Session
from debug_utils import debug_gps_init


class GPS:
    def __init__(self, session: Session, socket: str='/etc/default/gpsd'):
        # Store reference to session as attribute
        self.session = session
        self.socket = socket

        # Connect to GPS
        os.environ["GPSD_SOCKET"] = self.socket
        gpsd.connect()

        # Print debug info
        debug_gps_init(self)
        return

    def run_one_iteration(self) -> None:
        self.packet = gpsd.get_current()

        if self.packet.mode >= 2 and self.packet.lat != 'n/a' and self.packet.lon != 'n/a':
            # Assign values to shared geolocation attributes
            self.session.latitude.value = self.packet.lat
            self.session.longitude.value = self.packet.lon
            self.session.timestamp.value = time.time()

            return

        # Otherwise, raise an exception
        raise ValueError("No GPS data found")


    def get_location(self) -> None:
        while True:
            try:
                self.run_one_iteration()
                time.sleep(1)
            except Exception:
                pass
            time.sleep(0.1)
        return


    def run(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)


    def __call__(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)
~                                                 