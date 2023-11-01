from typing import Iterable
from collections import deque
import threading

import av
import cv2


class VideoReader:
    def __init__(
        self,
        *,
        urls: Iterable=None,
        containers: Iterable=None,
        storages: Iterable=None,
        timeout: int=200,
        **kwargs):
        if urls is not None:
            self.from_urls(urls)
        else:
            self.from_containers(containers, storages)
        self.timeout = timeout
        self.exit_flag = False
        return
    
    def from_containers(self, containers: Iterable, storages: Iterable) -> None:
        self.containers = containers
        self.storages = storages
        self.iterators = []
        self.urls = None
        for container in self.containers:
            # [TODO]: Add proper handling of None iterator
            iterator = self.iterator_from_container(container)
            self.iterators.append(iterator)
        return
    
    def from_urls(self, urls: Iterable) -> None:
        self.urls = urls
        self.containers = []
        self.storages = []
        self.iterators = []
        for url in urls:
            container = av.open(url)
            iterator = self.iterator_from_container(container)
            storage = deque()
            if iterator is None:
                continue
            self.containers.append(container)
            self.storages.append(storage)
            self.iterators.append(iterator)
        self.exit_flag = False
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
    
    def reinit(self) -> None:
        self.close()
        if self.urls is None:
            raise ValueError("URLs are not set. Can't reinit the instance.")
        return self.from_urls(self.urls)
    
    def close(self) -> None:
        for container in self.containers:
            container.close()
        return
    
    @staticmethod
    def get_frame(iterator, storage: deque) -> None:
        if len(storage) > 1:
            storage.popleft()
        frame = next(iterator).reformat(format="bgr24")
        storage.append(frame)
        return
    
    def display(self) -> None:
        for i, storage in enumerate(self.storages):
            if not storage:
                continue
            frame = storage[-1]
            frame_data = frame.to_ndarray()
            cv2.imshow(f"Frame AV{i}", frame_data)
            k = cv2.waitKey(1)
            if k == ord("q"):
                self.exit_flag = True
                cv2.destroyAllWindows()
                break
        return
    
    def run(self) -> None:
        threads = []
        for iterator, storage in zip(self.iterators, self.storages):
            thread = threading.Thread(target=self.get_frame, kwargs={"iterator": iterator, "storage": storage})
            threads.append(thread)
            thread.start()
        for thread in threads:    
            thread.join(timeout=self.timeout/1000)
        return