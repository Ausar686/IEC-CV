from multiprocessing import Value, SimpleQueue

from iec_mgt_typing import Session


class StreamManager:

    def __init__(
        self, 
        session: Session,
        stream: str,
        camera: int
    ):
        # Initalize manager information
        self.session = session
        self.camera = camera

        # Unpack the stream data
        (
            width,
            height,
            device,
            weights,
            conf,
            line_height,
            max_age,
            min_hits,
            iou_threshold,
            num_frames_to_average
        ) = self.session.stream_tuple

        # Initialize attributes to store workers data
        self.reader_tuple = (stream,)
        self.preprocessor_tuple = (width, height)
        self.detector_tuple = (weights, conf, device)
        self.tracker_tuple = (line_height, max_age, min_hits, iou_threshold, num_frames_to_average)

        # Initialize counters
        self.count_in = Value("I", 0)
        self.count_out = Value("I", 0)

        # Initialize storages
        self.read_storage = SimpleQueue()
        self.preprocess_storage = SimpleQueue()
        self.detect_storage = SimpleQueue()
        self.logs_storage = SimpleQueue()
        return