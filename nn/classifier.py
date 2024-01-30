import time

import cv2
import numpy as np
import torch
from ultralytics import YOLO

from loggers import Log, create_log
from utils.debug import (
    debug_classifier_init,
    debug_classify_frame,
    debug_fail_classify_frame,
)
from utils.types import StreamManager


class Classifier:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (
            cls_weights,
            cls_threshold,
            cls_half,
            cls_mode,
            cls_shape,
            device,
        ) = self.manager.classifier_tuple

        # Set required attributes for door classifier
        self.type = "classifier"
        self.device = device
        self.cls_model = YOLO(cls_weights, task="classify")
        self.cls_threshold = cls_threshold
        self.cls_half = cls_half
        self.cls_mode = cls_mode
        self.cls_shape = cls_shape

        # Print debug info
        debug_classifier_init(self)
        return

    def classify(self) -> None:
        # If there are no frames to process, simply wait
        if self.manager.preprocess_door_storage.empty():
            time.sleep(0.01)
            return

        # Get preprocessed frame to perform detection on
        frame = self.manager.preprocess_door_storage.get()
        door = self.get_door_state(frame)

        # Put data into a shared storage (or report about issue)
        try:
            self.manager.door_storage.put(door)
            debug_classify_frame(self, door)
        except Exception as e:
            debug_fail_classify_frame(self, door, e)
            log = create_log(self.manager, "classifier_put_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return

    def get_door_state(self, frame: np.ndarray) -> int:
        # Get frame shape (h, w)
        imgsz = frame.shape[:2]
        # Convert to torch.tensor if necessary
        if self.cls_mode == "torch":
            frame = (
                torch.from_numpy(frame)
                .permute((2, 0, 1))
                .unsqueeze(0)
                .cuda()
                .type(torch.float16)/255
            )
        # Run classification on image
        res = self.cls_model(
            frame,
            verbose=False,
            half=self.cls_half,
            imgsz=imgsz
        )
        r = res[0]
        closed_prob = r.probs.data[0]
        if closed_prob > self.cls_threshold:
            door = 0 # Closed
        else:
            door = 1 # Open
        return door

    def process(self, *args, **kwargs) -> None:
        return self.classify(*args, **kwargs)

    def run(self, *args, **kwargs) -> None:
        return self.classify(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.classify(*args, **kwargs)
