import time

import cv2

from iec_mgt_typing import StreamManager
from log import Log, create_log


class Preprocessor:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (width, height) = self.manager.preprocessor_tuple

        # Set required attributes
        self.width = width
        self.height = height
        return


    def preprocess(self) -> None:
        # If there are no frames to preprocess, simply wait
        if self.manager.read_storage.empty():
            time.sleep(0.1)
            return

        # Get the frame for preprocessing
        frame = self.manager.read_storage.get()

        # Preprocess the frame
        frame = cv2.resize(frame, (self.width, self.height))

        # Put preprocessed frame into shared storage (or report an issue)
        try:
            self.manager.preprocess_storage.put(frame)
        except Exception as e:
            log = create_log(self.manager, "preprocessor_put_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return


    def run(self) -> None:
        return self.preprocess()


    def __call__(self) -> None:
        return self.preprocess()