from typing import Tuple
from collections import deque

import numpy as np
import torch
import cv2

from sort import Sort
from iec_mgt_typing import Session
from reader import VideoReader
from drawer import Drawer
from preprocessor import Preprocessor
from logger import Logger
from detect import Detector


class StreamManager:

    def __init__(
        self, 
        stream: str,
        session: Session,
        camera: int=0,
        device: int|str="cuda" if torch.cuda.is_available() else "cpu",
        width: int=640,
        height: int=640,
        line_height: int=320,
        num_frames_to_average: int=5
        ):
        self.session = session
        self.camera = camera
        self.device = device
        self.status = 0
        self.count_in = 0
        self.count_out = 0
        self.boxes = np.empty((0, 4))
        self.enter_line = (0, line_height, width, line_height)
        self.reader = VideoReader(stream, self)
        self.preprocessor = Preprocessor(self, width, height)
        self.detector = Detector(self.session.weights, self)
        # Initialize drawer attributes
        self.drawer = Drawer(self)
        self.window_name = f"CAM_{self.camera}"
        # Initialize tracker attributes
        self.tracker =  Sort(max_age=20, min_hits=3, iou_threshold=0.3)
        self.last_directions = {}
        self.previous_y_coords = {}
        self.num_frames_to_average = num_frames_to_average
        # Initialize logger 
        self.logger = Logger(self.session)
        return

    def read_frame(self) -> Tuple[bool, np.ndarray|None]:
        self.reader.read()
        return (True, self.reader.storage[-1]) if self.reader.storage else (False, None)

    def preprocess_frame(self, frame: np.ndarray=None) -> np.ndarray|None:
        if frame is None:
            return None
        frame = self.preprocessor.run(frame)
        return frame

    def detect_on_frame(self, frame: np.ndarray|None=None) -> np.ndarray:
        if frame is None:
            return np.empty(0, 4)
        detections = self.detector.run(frame)
        return detections

    def draw_frame(self, name: str, frame: np.ndarray) -> None:
        self.drawer.run(name, frame)
        return

    def update_status_by_id(self, obj_id: int, cy: float, avg_y: float) -> None:
        if avg_y < self.enter_line[1] and cy > self.enter_line[1]:
            if self.last_directions.get(obj_id) != 'down':
                self.count_in += 1
                self.last_directions[obj_id] = 'down'
                self.logger.log(camera=self.camera, event="enter")
        elif avg_y > self.enter_line[1] and cy < self.enter_line[1]:
            if self.last_directions.get(obj_id) != 'up':
                self.count_out += 1
                self.last_directions[obj_id] = 'up'
                self.logger.log(camera=self.camera, event="exit")
        return

    def update_counters(self) -> None:
        tracker_data = self.tracker.update(self.boxes)
        for elem in tracker_data:
            # Get y-coordinate of a bbox center
            x1, y1, x2, y2, obj_id = elem
            cy = (y1 + y2) // 2
            # Add y-coordinate to deque, related to this object id
            if obj_id not in self.previous_y_coords:
                self.previous_y_coords[obj_id] = deque(maxlen=self.num_frames_to_average)
            self.previous_y_coords[obj_id].append(cy)
            # Calculate the average y-coordinate among recent frames
            avg_y = sum(self.previous_y_coords[obj_id]) / len(self.previous_y_coords[obj_id])
            # Update counters
            self.update_status_by_id(obj_id, cy, avg_y)    
        return

    def run_one_iteration(self) -> None:
        ret, frame = self.read_frame()
        frame = self.preprocess_frame(frame)
        detections = self.detect_on_frame(frame)
        self.update_counters()
        # self.draw_frame(self.window_name, frame)
        cv2.waitKey(1)
        self.status += 1
        return