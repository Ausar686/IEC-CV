import threading
from datetime import datetime

import cv2

from logger import Logger
from stream_manager import StreamManager


class Session:

    def __init__(
        self,
        weights: str,
        bus_id: str=None,
        route_id: str=None,
        n_cameras: int=1,
        timeout: int=300
        ):
        # Initialize session identifiers: bus id, route id and session id
        self.bus_id = bus_id
        self.route_id = route_id
        self.session_id = self.make_session_id()
        # Initialize logging path for this session
        self.event_log_path = self.make_event_log_path()
        # Initialize session utilities
        self.weights = weights
        self.managers = [StreamManager(f"test{i+2}.mp4", self, camera=i+1) for i in range(n_cameras)]
        self.timeout = timeout
        self.status = 0
        self.logger = Logger(self)
        self.threads = []
        return

    def make_session_id(self) -> str:
        now = datetime.now()
        date_str = str(now.date())
        session_id = f"{date_str}_{self.bus_id}_{self.route_id}"
        return session_id

    def make_event_log_path(self) -> str:
        log_path = f"log_{self.session_id}.json"
        return log_path

    def run(self) -> None:
        while True:
            for manager in self.managers:
                manager.run_one_iteration()
            # self.threads.clear()
            # for manager in self.managers:
            #     thread = threading.Thread(target=manager.run_one_iteration)
            #     self.threads.append(thread)
            # for thread in self.threads: 
            #     thread.start()
            # for thread in self.threads:
            #     thread.join(timeout=self.timeout/1000)
            print(f"FRAME: {self.status}")
            print(f"IN: {self.count_in}")
            print(f"OUT: {self.count_out}")
            print(f"TOTAL: {self.count_total}")
            self.status += 1
            for manager in self.managers:
                n_frames = len(manager.reader.storage)
                if n_frames <= 1 and self.status > 1:
                    manager.logger.log(camera=manager.camera, event="reading error")
                if manager.status != self.status:
                    manager.status = self.status
                    self.logger.log(camera=manager.camera, event="stream error")
        cv2.destroyAllWindows()
        return

    @property
    def count_in(self):
        return sum([manager.count_in for manager in self.managers])

    @property
    def count_out(self):
        return sum([manager.count_out for manager in self.managers])

    @property
    def count_total(self):
        return self.count_in - self.count_out