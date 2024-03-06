from datetime import datetime
from typing import Callable

import numpy as np

from utils.types import (
    Classifier,
    Detector,
    GPS,
    Logger,
    Preprocessor,
    Session,
    StreamManager,
    Tracker,
    VideoReader,
    VideoWriter,
)


def _debug_wrapper(func: Callable) -> Callable:
    """
    This wrapper is used for internal purposes only.
    It adds supplementary information (current datetitime) to logs about flow
    and prints the log into standard output (or it's substitution if present).
    Note, that these logs are used for debug purposes only.
    They are not necessary for being sent to remote server.
    """
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        now = datetime.now()
        debug_str = f"[INFO]: {now} {res}"
        print(debug_str)
        return res
    return wrapper

def _debug_fail_wrapper(func: Callable) -> Callable:
    """
    This function is an analog for _debug_wrapper but for logging errors.
    """
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        now = datetime.now()
        debug_str = f"[ERROR]: {now} {res}"
        print(debug_str)
        return res
    return wrapper

@_debug_wrapper
def debug_session_init(session: Session) -> str:
    return f"Session initialized: ctx={session.ctx}."

@_debug_wrapper
def debug_processes_init(processes: dict) -> str:
    return f"Processes: {processes}."

@_debug_wrapper
def debug_processes_start(processes: dict) -> str:
    return f"Session started."

@_debug_wrapper
def debug_processes_finish(processes: dict) -> str:
    return f"Session finished."

@_debug_wrapper
def debug_manager_init(manager: StreamManager) -> str:
    return f"Manager for CAM{manager.camera} initialized: stream={manager.reader_tuple}."

@_debug_wrapper
def debug_reader_init(reader: VideoReader) -> str:
    return f"Reader for CAM{reader.manager.camera} initialized."

@_debug_wrapper
def debug_read_not_empty(reader: VideoReader) -> str:
    return f"Reader storage for CAM{reader.manager.camera} is not empty. Waiting..."

@_debug_wrapper
def debug_read_frame(reader: VideoReader) -> str:
    return f"Put frame from CAM{reader.manager.camera}."

@_debug_fail_wrapper
def debug_fail_read_frame(reader: VideoReader, e: Exception) -> str:
    return f"Failed to put frame from CAM{reader.manager.camera}: {e}"

@_debug_wrapper
def debug_preprocessor_init(preprocessor: Preprocessor) -> str:
    return f"Preprocessor for CAM{preprocessor.manager.camera} initialized."

@_debug_wrapper
def debug_preprocess_empty(preprocessor: Preprocessor) -> str:
    return f"Preprocessing storage for CAM{preprocessor.manager.camera} is empty. Waiting..."

@_debug_wrapper
def debug_preprocess_frame(preprocessor: Preprocessor) -> str:
    return f"Put preprocessed frame from CAM{preprocessor.manager.camera}."

@_debug_fail_wrapper
def debug_fail_preprocess_frame(preprocessor: Preprocessor, e: Exception) -> str:
    return f"Failed to put preprocessed frame from CAM{preprocessor.manager.camera}: {e}"

@_debug_wrapper
def debug_detector_init(detector: Detector) -> str:
    return f"Detector for CAM{detector.manager.camera} initialized."

@_debug_wrapper
def debug_detect_empty(detector: Detector) -> str:
    return f"Detection storage for CAM{detector.manager.camera} is empty. Waiting..."

@_debug_wrapper
def debug_detect_frame(detector: Detector, detections: np.ndarray) -> str:
    return f"Put {detections.shape[0]} detections from CAM{detector.manager.camera}"

@_debug_fail_wrapper
def debug_fail_detect_frame(detector: Detector, detections: np.ndarray, e: Exception) -> str:
    return f"Failed to put {detections.shape[0]} detections from CAM{detector.manager.camera}: {e}"

@_debug_wrapper
def debug_classifier_init(classifier: Classifier) -> str:
    return f"Classification for CAM{classifier.manager.camera} initialized."

@_debug_wrapper
def debug_classifier_empty(classifier: Classifier) -> str:
    return f"Classification storage for CAM{classifier.manager.camera} is empty. Waiting..."

@_debug_wrapper
def debug_classify_frame(classifier: Classifier, door: int) -> str:
    return f"Put door state {door} from CAM{classifier.manager.camera}"

@_debug_fail_wrapper
def debug_fail_classify_frame(detector: Detector, door: int, e: Exception) -> str:
    return f"Failed to put door state {door} from CAM{classifier.manager.camera}: {e}"

@_debug_wrapper
def debug_tracker_init(tracker: Tracker) -> str:
    return f"Tracker for CAM{tracker.manager.camera} initialized"

@_debug_wrapper
def debug_track_empty(tracker: Tracker) -> str:
    return f"Tracking storage for CAM{tracker.manager.camera} is empty. Waiting..."

@_debug_wrapper
def debug_track_event(tracker: Tracker, event_name: str) -> str:
    return f"Tracked {event_name} event from CAM{tracker.manager.camera}"

@_debug_wrapper
def debug_fail_track_event(tracker: Tracker, event_name: str, e: Exception) -> str:
    return f"Failed to put tracker event '{event_name}' from CAM{tracker.manager.camera} due to: {e}"

# @_debug_wrapper
# def debug_track_enter(tracker: Tracker) -> str:
#     return f"Tracked enter event from CAM{tracker.manager.camera}"

# @_debug_fail_wrapper
# def debug_fail_track_enter(tracker: Tracker, e: Exception) -> str:
#     return f"Failed to put enter event from CAM{tracker.manager.camera}"

# @_debug_wrapper
# def debug_track_exit(tracker: Tracker) -> str:
#     return f"Tracked exit event from CAM{tracker.manager.camera}"

# @_debug_fail_wrapper
# def debug_fail_track_exit(tracker: Tracker, e: Exception) -> str:
#     return f"Failed to put exit event from CAM{tracker.manager.camera}"

@_debug_wrapper
def debug_gps_init(gps: GPS) -> str:
    return f"GPS initialized."

@_debug_wrapper
def debug_gps_get_geolocation(gps: GPS, geolocation: dict) -> str:
    return f"Obtained geolocation: {geolocation}."

@_debug_wrapper
def debug_gps_fail_get_location(gps: GPS, e: Exception) -> str:
    return f"Failed to obtain geolocation: {e}"

@_debug_wrapper
def debug_logger_init(logger: Logger) -> str:
    return "Logger initialized."

@_debug_wrapper
def debug_writer_init(writer: VideoWriter) -> str:
    return f"Writer for CAM{writer.manager.camera} initialized."

@_debug_wrapper
def debug_writer_create(writer: VideoWriter) -> str:
    return f"Created cv2.VideoWriter for CAM{writer.manager.camera} and hour {writer.start_hour}."

@_debug_wrapper
def debug_write_empty(writer: VideoWriter) -> str:
    return f"Writer storage for CAM{writer.manager.camera} is empty. Waiting..."

@_debug_wrapper
def debug_write_frame(writer: VideoWriter) -> str:
    return f"Written frame from CAM{writer.manager.camera} to {writer.out_path}."

@_debug_fail_wrapper
def debug_fail_write_frame(writer: VideoWriter, e: Exception) -> str:
    return f"Failed to write frame from CAM{writer.manager.camera} to {writer.out_path}: {e}"