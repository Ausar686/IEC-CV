import time

from utils.debug import debug_manager_init
from utils.types import Session


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
        self.patience = 3

        # Unpack the stream data
        (
            width,
            height,
            device,
            detect_weights,
            detect_conf,
            detect_iou,
            detect_half,
            min_detection_square,
            max_bbox_sides_relation,
            line_height,
            tracker_max_age,
            tracker_min_hits,
            tracker_iou,
            num_frames_to_average,
            min_frames_to_count,
            max_tracked_objects,
            fourcc,
            fps,
            cls_weights,
            cls_threshold,
            cls_half,
            cls_mode,
            cls_shape,
        ) = session.stream_tuple

        # Make shape for detector
        detect_shape = (width, height)

        # Initialize attributes to store workers' data
        self.reader_tuple = (stream,)
        self.preprocessor_tuple = (detect_shape, cls_shape)
        self.detector_tuple = (
            detect_weights,
            detect_conf,
            detect_iou,
            detect_half,
            device,
            min_detection_square,
            max_bbox_sides_relation,
        )
        self.classifier_tuple = (
            cls_weights,
            cls_threshold,
            cls_half,
            cls_mode,
            cls_shape,
            device,
        )
        self.tracker_tuple = (
            width,
            height,
            line_height,
            tracker_max_age,
            tracker_min_hits,
            tracker_iou,
            num_frames_to_average,
            min_frames_to_count,
            max_tracked_objects,
        )
        self.writer_tuple = (fourcc, fps, width, height)

        # Initialize counters
        self.count_in = self.session.ctx.Value("I", 0)
        self.count_out = self.session.ctx.Value("I", 0)

        # Initialize storages
        self.read_storage = self.ctx.Queue()
        self.read_timestamp = self.ctx.Value("d", time.time())
        self.preprocess_storage = self.ctx.Queue()
        self.preprocess_door_storage = self.ctx.Queue()
        self.detect_storage = self.ctx.Queue()
        self.door_storage = self.ctx.Queue()
        self.logs_storage = self.ctx.Queue()
        self.write_storage = self.ctx.Queue()

        # Print debug info
        debug_manager_init(self)
        return

    def validate_reader(self) -> bool:
        """Validate VideoReader activity status."""
        return time.time() - self.read_timestamp.value < self.patience