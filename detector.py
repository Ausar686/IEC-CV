import time

import numpy as np
import torch
from ultralytics import YOLO

from debug_utils import (
    debug_detector_init,
    debug_detect_empty,
    debug_detect_frame,
    debug_fail_detect_frame,
)
from iec_mgt_typing import StreamManager
from log import Log, create_log


class Detector:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (
            weights,
            conf,
            detect_iou,
            device,
            min_detection_square,
            max_bbox_sides_relation,
        ) = self.manager.detector_tuple

        # Set required attributes
        self.type = "detector"
        self.model = YOLO(weights)
        self.conf = conf
        self.device = device
        self.iou = detect_iou
        self.min_square = min_detection_square
        self.max_sides_relation = max_bbox_sides_relation

        # Print debug info
        debug_detector_init(self)
        return

    def detect(self) -> None:
        # If there are no frames to process, simply wait
        if self.manager.preprocess_storage.empty():
            # debug_detect_empty(self)
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
            results = self.model(
                frame,
                conf=self.conf,
                device=self.device,
                iou=self.iou,
                verbose=False,
            )

        # Initialize storage for detections
        detections = np.empty((0, 4))

        # Results is a generator, so we iterate among it's elements
        # Note: DO NOT pass several images to Detector at once
        for r in results:
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
            break
        return detections

    def process(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)

    def run(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)
