from multiprocessing import Process

from iec_mgt_typing import StreamManager, Session, Log
from reader import VideoReader
from preprocessor import Preprocessor
from detector import Detector
from tracker import Tracker
from logger import Logger


def run_read(manager: StreamManager) -> None:
    reader = VideoReader(manager)
    while True:
        reader.run()
    return


def run_preprocess(manager: StreamManager) -> None:
    preprocessor = Preprocessor(manager)
    while True:
        preprocessor.run()
    return


def run_detect(manager: StreamManager) -> None:
    detector = Detector(manager)
    while True:
        detector.run()
    return


def run_track(manager: StreamManager) -> None:
    tracker = Tracker(manager)
    while True:
        tracker.run()
    return


def run_log(session: Session) -> None:
    logger = Logger(session)
    while True:
        logger.run()
    return


def run_session(session: Session) -> None:
    processes = {
        manager.camera: {
            "reader": Process(target=run_read, args=(manager,)),
            "preprocessor": Process(target=run_preprocess, args=(manager,)),
            "detector": Process(target=run_detect, args=(manager,)),
            "tracker": Process(target=run_track, args=(manager,)),
        } for manager in session.managers
    }
    processes["logger"] = {
        "log": Process(target=run_log, args=(session,))
    }
    for dct in processes.values():
        for process in dct.values():
            process.start()
    return