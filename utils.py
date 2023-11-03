from multiprocessing import Process

from iec_mgt_typing import StreamManager, Session, Log
from reader import VideoReader
from preprocessor import Preprocessor
from detector import Detector
from tracker import Tracker
from logger import Logger
from gps import GPS


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


def run_gps(session: Session) -> None:
    gps = GPS(session)
    while True:
        gps.run()
    return


def run_session(session: Session) -> None:
    # Initialize processes for session
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
    processes["gps"] = {
        "gps": Process(target=run_gps, args=(session,))
    }

    # Start all processes
    for dct in processes.values():
        for process in dct.values():
            process.start()