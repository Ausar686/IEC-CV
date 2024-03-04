import time
from typing import Iterable

# import av
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
        # self.container = av.open(stream)
        # self.iterator = self.iterator_from_container(self.container)

        # Print debug info
        debug_reader_init(self)
        return

    # def iterator_from_container(self, container: av.container) -> Iterable:
    #     """
    #     Gets a Python iterator from av.container to simplify interface
    #     """
    #     video_stream = None
    #     for stream in container.streams:
    #         if stream.type == 'video':
    #             video_stream = stream
    #             break
    #     if video_stream is None:
    #         return None
    #     container.flags |= av.container.Flags.DISCARD_CORRUPT
    #     iterator = iter(container.decode(video=video_stream.index))
    #     return iterator

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
        # If shared storage is not empty, simply wait
        if not self.manager.read_storage.empty():
            time.sleep(0.01)
            return

        # Get next frame
        frame = self.get_frame()

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
        # # Read next frame in raw format
        # raw_frame = next(self.iterator).reformat(format="bgr24")
        # # Convert frame to np.ndarray
        # frame = raw_frame.to_ndarray()
        ret, frame = self.cap.read()
        return frame

    def close(self) -> None:
        # # Release all reader resources
        # self.container.close()
        self.cap.release()
        return

    def release(self) -> None:
        return self.close()

    def run(self, *args, **kwargs) -> None:
        return self.read(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.read(*args, **kwargs)
