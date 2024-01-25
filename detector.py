import time

import cv2
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
            detect_weights,
            detect_conf,
            detect_iou,
            detect_half,
            device,
            min_detection_square,
            max_bbox_sides_relation,
            cls_weights,
            cls_threshold,
            cls_half,
            cls_mode,
            cls_shape,
        ) = self.manager.detector_tuple

        # Set required attributes for person detector
        self.type = "detector"
        self.detect_model = YOLO(detect_weights)
        self.detect_conf = detect_conf
        self.detect_iou = detect_iou
        self.detect_half = detect_half
        self.device = device
        self.min_square = min_detection_square
        self.max_sides_relation = max_bbox_sides_relation

        # Set required attributes for door classifier
        self.cls_model = YOLO(cls_weights)
        self.cls_threshold = cls_threshold
        self.cls_half = cls_half
        self.cls_mode = cls_mode
        self.cls_shape = cls_shape

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
        door = self.get_door_state(frame)

        # Put data into a shared storage (or report about issue)
        try:
            self.manager.detect_storage.put(detections)
            self.manager.door_storage.put(door)
            debug_detect_frame(self, detections, door)
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

    def get_door_state(self, frame: np.ndarray) -> None:
        # Crop parts of the image, which contain the door 
        height, width, _ = frame.shape
        third_width = width // 3
        left_door = frame[:, :third_width]
        right_door = frame[:, -third_width:]
        image = np.hstack([left_door, right_door])
        if self.cls_shape is not None:
            image = cv2.resize(image, self.cls_shape)
        if self.cls_mode == "torch":
            image = (
                torch.from_numpy(image)
                .permute((2, 0, 1))
                .unsqueeze(0)
                .cuda()
            )
        # Run classification on image
        res = self.cls_model(image, verbose=False, half=self.cls_half)
        r = res[0]
        closed_prob = r.probs.data[0]
        if closed_prob > self.cls_threshold:
            door = 0 # Closed
        else:
            door = 1 # Open
        return door

    def process(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)

    def run(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.detect(*args, **kwargs)
