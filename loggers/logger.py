import json
import time

from utils.debug import debug_logger_init
from utils.types import Session, Log


class Logger:

    def __init__(self, session: Session):
        # Store reference to session as an attribute
        self.session = session

        # Initialize required attributes
        self.log_path = self.session.event_log_path

        # Print debug info
        debug_logger_init(self)
        return

    def write_log(self, log: Log) -> None:
        data = log.to_json()
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            if log_file.tell():
                data_str = ",\n" + json.dumps(data, indent=4)
            else:
                data_str = json.dumps(data, indent=4)
            log_file.write(data_str)
        return

    def log(self) -> None:
        for manager in self.session.managers:
            if manager.logs_storage.empty():
                time.sleep(0.01)
                continue
            log = manager.logs_storage.get()
            self.write_log(log)
        return

    def run(self, *args, **kwargs) -> None:
        return self.log(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.log(*args, **kwargs)
