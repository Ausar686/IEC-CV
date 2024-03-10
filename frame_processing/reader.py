import time
from typing import Iterable

import cv2
import numpy as np

from loggers import Log, create_log
from utils.debug import (
    debug_reader_init,
    debug_read_frame,
    debug_fail_read_frame,
)
from utils.types import StreamManager


class VideoReader:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (stream,) = self.manager.reader_tuple

        # Set required attributes
        self.type = "reader"
        self.cap = cv2.VideoCapture(stream)

        # Print debug info
        debug_reader_init(self)
        return

    def read(self) -> None:
        """
        Wrapper around '_read' method, that handles exceptions, 
        like KeyboardInterrupt.
        """
        try:
            return self._read()
        except:
            self.release()
            raise

    def _read(self) -> None:
        # Get next frame
        frame = self.get_frame()

        # # If shared storage is not empty, simply wait
        # # Add this only if your model is very slow.
        # # Note, that OpenCV and RTSP are trciky in terms of time and sync.
        # # So, sleeping even for 1ms can lead to frame corruption/crashes.
        # if not self.manager.read_storage.empty():
        #     time.sleep(0.001)
        #     return

        # Put the frame into shared storage (or report an issue)
        try:
            self.manager.read_storage.put(frame)
            self.manager.read_timestamp.value = time.time()
            debug_read_frame(self)
        except Exception as e:
            debug_fail_read_frame(self, e)
            log = create_log(self.manager, "reader_put_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return

    def get_frame(self) -> np.ndarray:
        ret, frame = self.cap.read()
        return frame

    def close(self) -> None:
        # Release all reader resources
        self.cap.release()
        return

    def release(self) -> None:
        return self.close()

    def run(self, *args, **kwargs) -> None:
        return self.read(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.read(*args, **kwargs)
