from typing import List, Tuple
from datetime import datetime
import multiprocessing as mp
import time

import torch

from stream_manager import StreamManager
from debug_utils import debug_session_init


class Session:

    def __init__(
        self,
        *,
        bus_id: str=None,
        route_id: str=None,
        n_cameras: int=1,
        streams: List[str]=None,
        width: int=640,
        height: int=640,
        weights: str=None,
        conf: float=0.3,
        device: int|str="cuda" if torch.cuda.is_available() else "cpu",
        line_height: int=320,
        max_age: int=20,
        min_hits: int=3,
        iou_threshold: float=0.3,
        num_frames_to_average: int=5,
        patience: float=30,
    ):
        # Check for wrong input
        if weights is None:
            raise ValueError("'weights' keyword argument should be not None.")
        if len(streams) != n_cameras:
            raise ValueError(f"Provided {len(streams)} streams for {n_cameras} cameras.")

        # Initialize session identifiers: bus id, route id and session id
        self.bus_id = bus_id
        self.route_id = route_id
        self.session_id = self.make_session_id()

        # Initialize logging path for this session
        self.event_log_path = self.make_event_log_path()

        # # Initialize shared geolocation storages as attributes
        self.ctx = mp.get_context("spawn")
        self.latitude = self.ctx.Value("d", 0)
        self.longitude = self.ctx.Value("d", 0)
        self.timestamp = self.ctx.Value("d", 0)

        # Initialize geolocation abscence patience
        self.patience = patience

        # # Initialize attribute for stream data storage
        self.stream_tuple = (
            width,
            height,
            device,
            weights,
            conf,
            line_height,
            max_age,
            min_hits,
            iou_threshold,
            num_frames_to_average
        )

        # Initialize stream managers
        self.managers = [
            StreamManager(self, stream, camera)
                for camera, stream in enumerate(streams, 1)
        ]

        # Print debug info
        debug_session_init(self)
        return


    def make_session_id(self) -> str:
        # Make session_id based on bus_id, route_id and current date
        now = datetime.now()
        date_str = str(now.date())
        session_id = f"{date_str}_{self.bus_id}_{self.route_id}"
        return session_id


    def make_event_log_path(self) -> str:
        # Make path for file with logs based on session_id
        log_path = f"log_{self.session_id}.json"
        return log_path
        

    @property
    def geolocation(self) -> Tuple[float]:
        # Get current timestamnp
        timestamp = time.time()

        # If previous geolocation update was too far ago, return None
        if timestamp - self.timestamp.value > self.patience:
            return None

        # Return stored geolocation otherwise
        return (self.latitude.value, self.longitude.value)


    @property
    def count_in(self) -> int:
        return sum([manager.count_in.value for manager in self.managers])


    @property
    def count_out(self) -> int:
        return sum([manager.count_out.value for manager in self.managers])


    @property
    def count_total(self) -> int:
        return self.count_in - self.count_out
