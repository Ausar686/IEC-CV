from typing import Tuple
from datetime import datetime

from iec_mgt_typing import StreamManager


class Log:

    def __init__(
        self,
        timestamp: datetime=None,
        camera: int=None,
        route_id: str=None,
        bus_id: str=None,
        session_id: str=None,
        event: str=None,
        error: Exception=None,
        geolocation: Tuple[float]=None
    ):
        self.start_date = datetime(1970, 1, 1)
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
        self.camera = camera
        self.route_id = route_id
        self.bus_id = bus_id
        self.session_id = session_id
        self.event = event
        self.error = error
        if geolocation is None:
            self.geolocation = (None, None)
        else:
            self.geolocation = geolocation
        return


    @property
    def total_seconds(self) -> float:
        return (self.timestamp - self.start_date).total_seconds()


    @property
    def date(self) -> str:
        return str(self.timestamp.date())


    @property
    def time(self) -> str:
        return str(self.timestamp.time())


    @property
    def latitude(self) -> float|None:
        return self.geolocation[0]


    @property
    def longitude(self) -> float|None:
        return self.geolocation[1]


    def to_json(self) -> dict:
        data = {
            "timestamp": self.total_seconds,
            "date": self.date,
            "time": self.time,
            "camera": self.camera,
            "route_id": self.route_id, 
            "bus_id": self.bus_id,
            "session_id": self.session_id,
            "event": self.event,
            "error": self.error,
            "geolocation": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            }
        }
        return data


def create_log(manager: StreamManager, event: str, error: Exception=None) -> Log:
    log = Log(
        camera=manager.camera,
        route_id=manager.session.route_id,
        bus_id=manager.session.bus_id,
        session_id=manager.session.session_id,
        event=event,
        error=error,
        geolocation=manager.session.geolocation
    )
    return log