from typing import Iterable
import time

import av

from iec_mgt_typing import StreamManager
from log import Log, create_log


class VideoReader:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (stream,) = self.manager.reader_tuple

        # Set required attributes
        self.container = av.open(stream)
        self.iterator = self.iterator_from_container(self.container)
        return


    def iterator_from_container(self, container) -> Iterable:
        # Get a simple Python iterator from av.container to simplify interface
        video_stream = None
        for stream in container.streams:
            if stream.type == 'video':
                video_stream = stream
                break
        if video_stream is None:
            return None
        iterator = iter(container.decode(video=video_stream.index))
        return iterator


    def read(self) -> None:
        # If shared storage is not empty, simply wait
        if not self.manager.read_storage.empty():
            time.sleep(0.1)
            return

        # Read next frame in raw format
        raw_frame = next(self.iterator).reformat(format="bgr24")

        # Convert frame to np.ndarray
        frame = raw_frame.to_ndarray()

        # Put the frame into shared storage (or report an issue)
        try:
            self.manager.read_storage.put(frame)
        except Exception as e:
            log = create_log(self.manager, "reader_put_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return


    def close(self) -> None:
        self.container.close()
        return


    def release(self) -> None:
        return self.close()


    def run(self) -> None:
        return self.read()


    def __call__(self) -> None:
        return self.read()