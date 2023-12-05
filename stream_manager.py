from debug_utils import debug_manager_init
from iec_mgt_typing import Session


class StreamManager:

    def __init__(
        self, 
        session: Session,
        stream: str,
        camera: int
    ):
        # Store a reference to session as an attribute
        self.session = session
        
        # Initalize manager information
        self.camera = camera
        self.ctx = self.session.ctx

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
            num_frames_to_average,
            max_tracked_objects,
            fourcc,
            fps,
        ) = session.stream_tuple

        # Initialize attributes to store workers' data
        self.reader_tuple = (stream,)
        self.preprocessor_tuple = (width, height)
        self.detector_tuple = (weights, conf, device)
        self.tracker_tuple = (
            line_height,
            max_age,
            min_hits,
            iou_threshold,
            num_frames_to_average,
            max_tracked_objects,
        )
        self.writer_tuple = (fourcc, fps, width, height)

        # Initialize counters
        self.count_in = self.session.ctx.Value("I", 0)
        self.count_out = self.session.ctx.Value("I", 0)

        # Initialize storages
        self.read_storage = self.ctx.Queue()
        self.preprocess_storage = self.ctx.Queue()
        self.detect_storage = self.ctx.Queue()
        self.logs_storage = self.ctx.Queue()
        self.write_storage = self.ctx.Queue()

        # Print debug info
        debug_manager_init(self)
        return