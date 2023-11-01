import math
from datetime import datetime
from collections import deque

import numpy as np
from ultralytics import YOLO
import cv2
import pyresearch

from sort import *
from logger import Logger


class Session:
    def __init__(
        self,
        video_path: str,
        model: YOLO,
        route_id: str=None,
        bus_id: str=None,
        conf: float=0.3
        ):
        self.cap = cv2.VideoCapture(video_path)
        self.model = YOLO(model)

        # Initialize session identifiers: bus id, route id and session id
        self.bus_id = bus_id
        self.route_id = route_id
        self.session_id = self.make_session_id()

        # Initialize logging path for this session
        self.event_log_path = self.make_event_log_path()

        # Initialize event logger for this session
        self.logger = Logger(self)

        self.central_line = [0, 320, 640, 320]

        self.tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

        self.conf = conf

        self.last_direction = {}
        self.previous_y_coords = {}
        self.num_frames_to_average = 5

        # Initalize passengers' counters
        self.count_up = 0
        self.count_down = 0
        return

    def make_session_id(self) -> str:
        now = datetime.now()
        date_str = str(now.date())
        session_id = f"{date_str}_{self.bus_id}_{self.route_id}"
        return session_id

    def make_event_log_path(self) -> str:
        log_path = f"log_{self.session_id}.json"
        return log_path
        
    def read_video(self):
        success, img = self.cap.read()
        if not success:
            return None
        img = cv2.resize(img, (640, 640))
        return img
        
    def display_video(self, img):
        cv2.line(img, (self.central_line[0], self.central_line[1]), (self.central_line[2], self.central_line[3]), (0, 0, 255), 5)
        cv2.putText(img, f'People Out: {self.count_up}', (20, 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f'People In: {self.count_down}', (20, 110), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
        cv2.imshow("VideoDisplay", img)
        cv2.waitKey(1)
        return


    def process_frame(self, img):
        results = self.model(img, conf=self.conf)
        return results


    def process_and_draw_boxes(self, results, img):
        for r in results:
            boxes = r.boxes
            detections = np.empty((0, 4))
            xyxy = boxes.xyxy.cpu().numpy().astype(int)
            detections = np.vstack((detections, xyxy))
            for rect in xyxy:
                x1, y1, x2, y2 = rect
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        return detections

    def process_tracker_data(self, resultsTracker):
        for result in resultsTracker:
            x1, y1, x2, y2, id = result
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            
            if id not in self.previous_y_coords:
                self.previous_y_coords[id] = deque()
            self.previous_y_coords[id].append(cy)
            if len(self.previous_y_coords[id]) > self.num_frames_to_average:
                self.previous_y_coords[id].popleft()

            avg_previous_y = sum(self.previous_y_coords[id]) / len(self.previous_y_coords[id])

            if avg_previous_y < self.central_line[1] and cy > self.central_line[1]:
                if self.last_direction.get(id) != 'down':
                    self.count_down += 1
                    self.last_direction[id] = 'down'
                    self.logger.log(camera=0, event="enter") # Replace this with actual camera number
            elif avg_previous_y > self.central_line[1] and cy < self.central_line[1]:
                if self.last_direction.get(id) != 'up':
                    self.count_up += 1
                    self.last_direction[id] = 'up'
                    self.logger.log(camera=0, event="exit") # Replace this with actual camera number
                    
        return

    def run_one_iteration(self, img: np.ndarray) -> None:
        results = self.model(img, conf=self.conf, stream=True)   
        detections = self.process_and_draw_boxes(results, img)
        print(detections.shape)
        resultsTracker = self.tracker.update(detections)
        self.process_tracker_data(resultsTracker)
        self.display_video(img)
        return
        
    def run(self):
        while True:
            img = self.read_video()
            if img is None:
                break
            self.run_one_iteration(img)
        cv2.destroyAllWindows()
