import json
import time

from iec_mgt_typing import Session, Log


class Logger:

    def __init__(self, session: Session):
        self.session = session
        self.log_path = self.session.event_log_path
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
                time.sleep(0.1)
                continue
            log = manager.logs_storage.get()
            self.write_log(log)
        return


    def run(self) -> None:
        return self.log()


    def __call__(self) -> None:
        return self.log()