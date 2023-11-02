from typing import List
from datetime import datetime

import torch

from stream_manager import StreamManager


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

        # Initialize attribute for stream data storage
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
            StreamManager(self, stream, camera) for camera, stream in enumerate(streams, 1)
        ]
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
    def count_in(self) -> int:
        return sum([manager.count_in.value for manager in self.managers])


    @property
    def count_out(self) -> int:
        return sum([manager.count_out.value for manager in self.managers])


    @property
    def count_total(self) -> int:
        return self.count_in - self.count_out