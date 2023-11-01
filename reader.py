from typing import Iterable
from collections import deque

import av
import numpy as np

from iec_mgt_typing import StreamManager


class VideoReader:

    def __init__(self, stream: str, manager: StreamManager=None):
        self.container = av.open(stream)
        self.iterator = self.iterator_from_container(self.container)
        self.storage = deque()
        self.manager = manager
        return

    def iterator_from_container(self, container) -> Iterable:
        video_stream = None
        for stream in container.streams:
            if stream.type == 'video':
                video_stream = stream
                break
        if video_stream is None:
            return None
        iterator = iter(container.decode(video=video_stream.index))
        return iterator

    def read(self) -> np.ndarray:
        if len(self.storage) > 1:
            self.storage.popleft()
        raw_frame = next(self.iterator).reformat(format="bgr24")
        frame = raw_frame.to_ndarray()
        self.storage.append(frame)
        return True, frame

    def close(self) -> None:
        self.container.close()
        return

    def release(self) -> None:
        return self.close()

    def run(self) -> np.ndarray:
        return self.read()

    def __call__(self) -> np.ndarray:
        return self.read()