from collections import deque
import time

from loggers import Log, create_log
from utils.debug import (
    debug_tracker_init,
    debug_track_empty,
    debug_track_exit,
    debug_fail_track_exit,
    debug_track_enter,
    debug_fail_track_enter,
)
from utils.types import StreamManager
from .sort import Sort


class Tracker:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (
            width,
            height,
            line_height,
            max_age,
            min_hits,
            tracker_iou,
            num_frames_to_average,
            min_frames_to_count,
            max_tracked_objects,
        ) = self.manager.tracker_tuple

        # Initialize tracker
        self.tracker = Sort(
            max_age=max_age,
            min_hits=min_hits,
            iou_threshold=tracker_iou
        )

        # Initialize frame parameters
        self.width = width
        self.height = height
        
        # Initialize line coordinates
        self.delta_y = self.height // 20
        self.delta_x = self.width // 6
        self.line_height = line_height
        self.line_height_low = self.line_height - self.delta_y
        self.line_height_high = self.line_height + self.delta_y
        self.x_min = self.delta_x
        self.x_max = self.width - self.delta_x

        # Initialize worker type
        self.type = "tracker"

        # Initialize parameters for tracking
        self.num_frames_to_average = num_frames_to_average
        self.max_tracked_objects = max_tracked_objects
        self.last_direction = {}
        self.previous_y = {}
        self.previous_low_y = {}
        self.previous_high_y = {}
        self.frame_counter = 0
        self.min_frames_to_count = min_frames_to_count

        # Print debug info
        debug_tracker_init(self)
        return

    def update_counters(self) -> None:
        # If there is no data to process, simply wait 
        if (
            self.manager.detect_storage.empty()
            or self.manager.door_storage.empty()
        ):
            time.sleep(0.01)
            return

        # Update frame counter
        self.frame_counter += 1

        # Get bboxes of detected objects
        boxes = self.manager.detect_storage.get()

        # Get door state
        door = self.manager.door_storage.get()

        # Update Sort tracker
        tracker_data = self.tracker.update(boxes)

        # Iterate over elements in updated data 
        for elem in tracker_data:
            # Get y-coordinate of a bbox center
            x1, y1, x2, y2, obj_id = elem
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Check object dynamics
            if obj_id in self.previous_y and door:
                # Update counters
                self.update_status_by_id(obj_id, cx, cy, y1, y2)
            elif obj_id not in self.previous_y:
                self.previous_y[obj_id] = deque(
                    maxlen=self.num_frames_to_average
                )
                self.previous_low_y[obj_id] = deque(
                    maxlen=self.num_frames_to_average
                )
                self.previous_high_y[obj_id] = deque(
                    maxlen=self.num_frames_to_average
                )
            self.previous_y[obj_id].append(cy)
            self.previous_low_y[obj_id].append(y2)
            self.previous_high_y[obj_id].append(y1)

        # Keep storages' size limited
        self.check_storages()
        return

    def update_status_by_id(
        self,
        obj_id: int,
        cx: float,
        cy: float,
        y1: float,
        y2: float
    ) -> None:
        # Check if the person's x-coordinate is inside the area
        if not (self.x_min <= cx <= self.x_max):
            return

        # Calculate the average y-coordinate among recent frames
        avg_y = sum(self.previous_y[obj_id]) / len(self.previous_y[obj_id])
        avg_low_y = sum(self.previous_low_y[obj_id]) / len(self.previous_low_y[obj_id])
        avg_high_y = sum(self.previous_high_y[obj_id]) / len(self.previous_high_y[obj_id])

        # Person is entering the bus 
        if avg_y < self.line_height and cy > self.line_height:
            self.process_enter_event(obj_id)

        # Person is exiting the bus
        elif avg_y > self.line_height and cy < self.line_height:
            self.process_exit_event(obj_id)

        # Person has been standing next to the door and is exiting now
        elif avg_low_y > self.line_height_low and y2 < self.line_height_low:
            self.process_exit_event(obj_id)

        # Person has entered too fast, and detector failed
        # to recognize him quickly
        elif avg_high_y < self.line_height_high and y1 > self.line_height_high:
            self.process_enter_event(obj_id)
        return

    def process_enter_event(self, obj_id: int) -> None:
        obj_dir_data = self.last_direction.get(obj_id) 
        # Check for enter conditions
        if (
            obj_dir_data is None 
            or (
                obj_dir_data[0] == "up" 
                and self.frame_counter - obj_dir_data[1] >= self.min_frames_to_count
            )
        ):
            # Increment counter and write logs
            self.manager.count_in.value += 1
            self.last_direction[obj_id] = ("down", self.frame_counter)
            # Put data into a shared storage (or report about issue)
            try:
                log = create_log(self.manager, "enter")
                self.manager.logs_storage.put(log)
                debug_track_enter(self)
            except Exception as e:
                debug_fail_track_enter(self, e)
                log = create_log(self.manager, "tracker_put_error", e)
                try:
                    self.manager.logs_storage.put(log)
                except Exception:
                    pass
        return

    def process_exit_event(self, obj_id: int) -> None:
        obj_dir_data = self.last_direction.get(obj_id) 
        # Check for exit conditions
        if (
            obj_dir_data is None 
            or (
                obj_dir_data[0] == "down" 
                and self.frame_counter - obj_dir_data[1] >= self.min_frames_to_count
            )
        ):
            # Increment counter and write logs
            self.manager.count_out.value += 1
            self.last_direction[obj_id] = ("up", self.frame_counter)
            # Put data into a shared storage (or report about issue)
            try:
                log = create_log(self.manager, "exit")
                self.manager.logs_storage.put(log)
                debug_track_exit(self)
            except Exception as e:
                debug_fail_track_exit(self, e)
                log = create_log(self.manager, "tracker_put_error", e)
                try:
                    self.manager.logs_storage.put(log)
                except Exception:
                    pass
        return

    def check_storages(self) -> None:
        extra_coords = len(self.previous_y) - self.max_tracked_objects
        extra_dirs = len(self.last_direction) - self.max_tracked_objects
        if extra_coords > 0:
            for center in list(self.previous_y.keys())[:extra_coords]:
                self.previous_y.pop(center)
                self.previous_low_y.pop(center)
                self.previous_high_y.pop(center)
        if extra_dirs > 0:
            for obj_id in list(self.last_direction.keys())[:extra_dirs]:
                self.last_direction.pop(obj_id)
        return

    def track(self, *args, **kwargs) -> None:
        return self.update_counters(*args, **kwargs)

    def run(self, *args, **kwargs) -> None:
        return self.update_counters(*args, **kwargs)

    def __call__(self, *args, **kwargs) ->  None:
        return self.update_counters(*args, **kwargs)
