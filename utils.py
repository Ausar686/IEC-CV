from datetime import datetime
import multiprocessing as mp
import os
import time

from debug_utils import (
    debug_processes_init,
    debug_processes_start,
    debug_processes_finish,
)
from detector import Detector
from gps import GPS
from iec_mgt_typing import StreamManager, Session, Log
from logger import Logger
from preprocessor import Preprocessor
from reader import VideoReader
from tracker import Tracker
from writer import VideoWriter


def set_environment(**kwargs) -> None:
    for key, path in kwargs.items():
        os.makedirs(path, exist_ok=True)
        os.environ[key] = path
    return


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


def run_write(manager: StreamManager) -> None:
    writer = VideoWriter(manager)
    while True:
        writer.run()
    return


def run_session(session: Session) -> None:
    processes = _make_processes(session)
    _start_processes(processes)
    _join_processes(processes, session)
    return


def _make_processes(session: Session) -> dict:
    # Initialize processes for session
    processes = {
        manager.camera: {
            "reader": manager.ctx.Process(
                target=run_read,
                args=(manager,)
            ),
            "preprocessor": manager.ctx.Process(
                target=run_preprocess,
                args=(manager,)
            ),
            "detector": manager.ctx.Process(
                target=run_detect,
                args=(manager,)
            ),
            "tracker": manager.ctx.Process(
                target=run_track,
                args=(manager,)
            ),
            "writer": manager.ctx.Process(
                target=run_write,
                args=(manager,)
            ),
        } for manager in session.managers
    }
    processes["logger"] = {
        "log": session.ctx.Process(
            target=run_log,
            args=(session,)
        )
    }
    processes["gps"] = {
        "gps": session.ctx.Process(
            target=run_gps,
            args=(session,)
        )
    }
    debug_processes_init(processes)
    return processes


def _start_processes(processes: dict) -> None:
    # Start all processes
    for dct in processes.values():
        for process in dct.values():
            process.start()
    debug_processes_start(processes)
    return


def _join_processes(processes: dict, session:Session) -> None:
    # Wait for a session stop hour (sleep to lower CPU usage)
    while not session.is_over:
        time.sleep(1)
    # Kill all the remaining processes and join them
    for dct in processes.values():
        for process in dct.values():
            process.kill()
            process.join()
    debug_processes_finish(processes)
    return