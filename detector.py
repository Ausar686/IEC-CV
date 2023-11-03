import time

import numpy as np
from ultralytics import YOLO
import torch

from iec_mgt_typing import StreamManager
from log import Log, create_log


class Detector:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (weights, conf, device) = self.manager.detector_tuple

        # Set required attributes
        self.model = YOLO(weights)
        self.conf = conf
        self.device = device
        return


    def detect(self) -> None:
        # If there are no frames to process, simply wait
        # if self.manager.preprocess_storage.empty():
        #     time.sleep(0.1)
        #     return

        # Get preprocessed frame to perform detection on
        frame = self.manager.preprocess_storage.get()

        # Perform detection
        with torch.no_grad():
            results = self.model(frame, conf=self.conf, device=self.device, verbose=False)

        # Results is a generator, so we iterate among it's elements
        for r in results: # DO NOT pass several images to Detector at once
            detections = np.empty((0, 4))

            # Convert to numpy array of integers (to be able to draw bboxes)
            xyxy = r.boxes.xyxy.cpu().numpy()
            detections = np.vstack((detections, xyxy))

            # Put data into a shared storage (or report about issue)
            try:
                self.manager.detect_storage.put(detections)
            except Exception as e:
                log = create_log(self.manager, "detector_put_error", e)
                try:
                    self.manager.logs_storage.put(log)
                except Exception:
                    pass
            return


    def process(self) -> None:
        return self.detect()


    def run(self) -> None:
        return self.detect()


    def __call__(self) -> None:
        return self.detect()