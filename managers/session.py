from datetime import datetime
from typing import List, Tuple
import multiprocessing as mp
import os
import time

import torch

from managers.manager import StreamManager
from utils.debug import debug_session_init


class Session:

    def __init__(self, **kwargs):
        # Unpack arguments
        bus_id = kwargs.get("bus_id", None)
        route_id = kwargs.get("route_id", None)
        n_cameras = kwargs.get("n_cameras", 1)
        streams = kwargs.get("streams", [])
        width = kwargs.get("width", 640)
        height = kwargs.get("height", 640)
        detect_weights = kwargs.get("detect_weights", None)
        detect_conf = kwargs.get("detect_conf", 0.45)
        detect_iou = kwargs.get("detect_iou", 0.01)
        detect_half = kwargs.get("detect_half", True)
        min_detection_square = kwargs.get("min_detection_square", 0)
        max_bbox_sides_relation = kwargs.get("max_bbox_sides_relation", float("inf"))
        device = kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        line_height = kwargs.get("line_height", 130)
        tracker_max_age = kwargs.get("tracker_max_age", 60)
        tracker_min_hits = kwargs.get("tracker_min_hits", 1)
        tracker_iou = kwargs.get("tracker_iou", 0.02)
        num_frames_to_average = kwargs.get("num_frames_to_average", 5)
        min_frames_to_count = kwargs.get("min_frames_to_count", 500)
        max_tracked_objects = kwargs.get("max_tracked_objects", 100)
        patience = kwargs.get("patience", 120)
        fourcc = kwargs.get("fourcc", "mp4v")
        fps = kwargs.get("fps", 30)
        stop_hour = kwargs.get("stop_hour", 2)
        cls_weights = kwargs.get("cls_weights", None)
        cls_threshold = kwargs.get("cls_threshold", 0.25)
        cls_half = kwargs.get("cls_half", True)
        cls_mode = kwargs.get("cls_mode", "torch")
        cls_shape = kwargs.get("cls_shape", None)
        gps_api_key = kwargs.get("gps_api_key", os.environ.get("GPS_API_KEY"))

        # Check for wrong input
        if detect_weights is None or cls_weights is None:
            raise ValueError(
                "Keyword arguments 'detect_weights'and 'cls_weights' ",
                "should be not None."
            )
        if len(streams) != n_cameras:
            raise ValueError(f"Provided {len(streams)} streams for {n_cameras} cameras.")

        # Initialize session identifiers: bus id, route id and session id
        self.bus_id = bus_id
        self.route_id = route_id
        self.session_id = self.make_session_id()

        # Initialize parameters for time management
        self.stop_hour = stop_hour
        
        # Initialize GPS parameters
        self.gps_api_key = gps_api_key

        # Initialize logging path for this session
        self.event_log_path = self.make_event_log_path()

        # Initialize shared geolocation storages as attributes
        self.ctx = mp.get_context("spawn")
        self.latitude = self.ctx.Value("d", 0)
        self.longitude = self.ctx.Value("d", 0)
        self.timestamp = self.ctx.Value("d", time.time())

        # Initialize geolocation abscence patience
        self.patience = patience

        # Initialize attribute for stream data storage
        self.stream_tuple = (
            width,
            height,
            device,
            detect_weights,
            detect_conf,
            detect_iou,
            detect_half,
            min_detection_square,
            max_bbox_sides_relation,
            line_height,
            tracker_max_age,
            tracker_min_hits,
            tracker_iou,
            num_frames_to_average,
            min_frames_to_count,
            max_tracked_objects,
            fourcc,
            fps,
            cls_weights,
            cls_threshold,
            cls_half,
            cls_mode,
            cls_shape,
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
        # Make path for file with logs based on 
        # session_id and "logs_dir" environment variable.
        filename = f"log_{self.session_id}.json"
        directory = os.environ.get("logs_dir", "/tmp")
        log_path = os.path.join(directory, filename)
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

    @property
    def is_over(self) -> bool:
        return datetime.now().time().hour == self.stop_hour