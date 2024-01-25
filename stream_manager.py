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

        # Initialize attributes to store workers' data
        self.reader_tuple = (stream,)
        self.preprocessor_tuple = (width, height)
        self.detector_tuple = (
            detect_weights,
            detect_conf,
            detect_iou,
            detect_half,
            device,
            min_detection_square,
            max_bbox_sides_relation,
            cls_weights,
            cls_threshold,
            cls_half,
            cls_mode,
            cls_shape,
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
        self.preprocess_storage = self.ctx.Queue()
        self.detect_storage = self.ctx.Queue()
        self.door_storage = self.ctx.Queue()
        self.logs_storage = self.ctx.Queue()
        self.write_storage = self.ctx.Queue()

        # Print debug info
        debug_manager_init(self)
        return