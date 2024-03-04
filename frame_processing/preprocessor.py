import time

import cv2
import numpy as np

from loggers import Log, create_log
from utils.debug import (
    debug_preprocessor_init,
    debug_preprocess_frame,
    debug_fail_preprocess_frame,
)
from utils.types import StreamManager


class Preprocessor:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (detect_shape, cls_shape) = self.manager.preprocessor_tuple

        # Set required attributes
        self.type = "preprocessor"
        self.detect_shape = detect_shape
        self.cls_shape = cls_shape

        # Print debug info
        debug_preprocessor_init(self)
        return


    def preprocess(self) -> None:
        # If there are no frames to preprocess, simply wait
        if self.manager.read_storage.empty():
            time.sleep(0.01)
            return

        # Get the frame for preprocessing
        frame = self.manager.read_storage.get()
        if frame is None:
            return

        # Preprocess the frame (classification)
        # Crop parts of the image, which contain the door 
        height, width, _ = frame.shape
        third_width = width // 3
        left_door = frame[:, :third_width]
        right_door = frame[:, -third_width:]
        image = np.hstack([left_door, right_door])
        cls_frame = cv2.resize(image, self.cls_shape)

        # Preprocess the frame (detection)
        detect_frame = cv2.resize(frame, self.detect_shape)

        # Put preprocessed frames into shared storages (or report an issue)
        try:
            self.manager.preprocess_storage.put(detect_frame)
            self.manager.preprocess_door_storage.put(cls_frame)
            self.manager.write_storage.put(detect_frame)
            debug_preprocess_frame(self)
        except Exception as e:
            debug_fail_preprocess_frame(self, e)
            log = create_log(self.manager, "preprocessor_put_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return


    def run(self, *args, **kwargs) -> None:
        return self.preprocess(*args, **kwargs)


    def __call__(self, *args, **kwargs) -> None:
        return self.preprocess(*args, **kwargs)
