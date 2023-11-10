import time

import cv2

from iec_mgt_typing import StreamManager
from log import Log, create_log
from debug_utils import (
    debug_preprocessor_init,
    debug_preprocess_empty,
    debug_preprocess_frame,
    debug_fail_preprocess_frame,
)


class Preprocessor:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (width, height) = self.manager.preprocessor_tuple

        # Set required attributes
        self.type = "preprocessor"
        self.width = width
        self.height = height

        # Print debug info
        debug_preprocessor_init(self)
        return


    def preprocess(self) -> None:
        # If there are no frames to preprocess, simply wait
        if self.manager.read_storage.empty():
            # debug_preprocess_empty(self)
            time.sleep(0.01)
            return

        # Get the frame for preprocessing
        frame = self.manager.read_storage.get()

        # Preprocess the frame
        frame = cv2.resize(frame, (self.width, self.height))

        # Put preprocessed frame into shared storage (or report an issue)
        try:
            self.manager.preprocess_storage.put(frame)
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
