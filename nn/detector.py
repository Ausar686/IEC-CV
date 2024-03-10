import time

from ultralytics import YOLO
import cv2
import numpy as np
import torch

from loggers import Log, create_log
from utils.debug import (
    debug_detector_init,
    debug_detect_frame,
    debug_fail_detect_frame,
)
from utils.types import StreamManager


class Detector:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (
            detect_weights,
            detect_conf,
            detect_iou,
            detect_half,
            device,
            min_detection_square,
            max_bbox_sides_relation,
        ) = self.manager.detector_tuple

        # Set required attributes for person detector
        self.type = "detector"
        self.detect_model = YOLO(detect_weights, task="detect")
        self.detect_conf = detect_conf
        self.detect_iou = detect_iou
        self.detect_half = detect_half
        self.device = device
        self.min_square = min_detection_square
        self.max_sides_relation = max_bbox_sides_relation

        # Print debug info
        debug_detector_init(self)
        return

    def detect(self) -> None:
        # If there are no frames to process, simply wait
        if self.manager.preprocess_storage.empty():
            time.sleep(0.01)
            return

        # Get preprocessed frame to perform detection on
        frame = self.manager.preprocess_storage.get()
        detections = self.get_detections(frame)

        # Put data into a shared storage (or report about issue)
        try:
            self.manager.detect_storage.put(detections)
            debug_detect_frame(self, detections)
        except Exception as e:
            debug_fail_detect_frame(self, detections, e)
            log = create_log(self.manager, "detector_put_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return

    def get_detections(self, frame: np.ndarray) -> np.ndarray:
        # Perform detection
        with torch.no_grad():
            results = self.detect_model(
                frame,
                conf=self.detect_conf,
                device=self.device,
                iou=self.detect_iou,
                verbose=False,
            )
            # Results is a list with 1 element
            r = results[0]

        # Initialize storage for detections
        detections = np.empty((0, 4))
        # Convert to numpy array of floats
        xyxy = r.boxes.xyxy.cpu().numpy()
        w = xyxy[:, 2] - xyxy[:, 0]
        h = xyxy[:, 3] - xyxy[:, 1]
        # Keep only big enough detections with 'square-like' forms
        cond1 = w * h > self.min_square
        cond2 = w / h < self.max_sides_relation
        cond3 = h / w < self.max_sides_relation
        cond = cond1 * cond2 * cond3
        xyxy = xyxy[cond]
        detections = np.vstack((detections, xyxy))
        return detections

    def process(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)

    def run(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)
