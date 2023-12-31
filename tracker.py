from collections import deque
import time

from debug_utils import (
    debug_tracker_init,
    debug_track_empty,
    debug_track_exit,
    debug_fail_track_exit,
    debug_track_enter,
    debug_fail_track_enter,
)
from iec_mgt_typing import StreamManager
from log import Log, create_log
from sort import Sort


class Tracker:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (
            line_height,
            max_age,
            min_hits,
            iou_threshold,
            num_frames_to_average,
            max_tracked_objects,
        ) = self.manager.tracker_tuple

        # Initialize tracker
        self.tracker = Sort(
            max_age=max_age,
            min_hits=min_hits,
            iou_threshold=iou_threshold
        )
        
        # Initialize line coordinates
        self.line_height = line_height

        # Initialize worker type
        self.type = "tracker"

        # Initialize parameters for tracking
        self.num_frames_to_average = num_frames_to_average
        self.max_tracked_objects = max_tracked_objects
        self.last_directions = {}
        self.previous_y_coords = {}

        # Print debug info
        debug_tracker_init(self)
        return

    def update_counters(self) -> None:
        # If there is no data to process, simply wait 
        if self.manager.detect_storage.empty():
            # debug_track_empty(self)
            time.sleep(0.01)
            return

        # Get bboxes of detected objects
        boxes = self.manager.detect_storage.get()

        # Update Sort tracker
        tracker_data = self.tracker.update(boxes)

        # Iterate over elements in updated data 
        for elem in tracker_data:
            # Get y-coordinate of a bbox center
            x1, y1, x2, y2, obj_id = elem
            cy = (y1 + y2) // 2

            # Append y-coordinate to deque, related to this object id
            if obj_id not in self.previous_y_coords:
                self.previous_y_coords[obj_id] = deque(
                    maxlen=self.num_frames_to_average
                )
            self.previous_y_coords[obj_id].append(cy)

            # Calculate the average y-coordinate among recent frames
            avg_y = sum(self.previous_y_coords[obj_id]) / len(self.previous_y_coords[obj_id])

            # Update counters
            self.update_status_by_id(obj_id, cy, avg_y)

        # Keep storages' size limited
        self.check_storages()
        return

    def update_status_by_id(self, obj_id: int, cy: float, avg_y: float) -> None:
        # Person is entering the bus 
        if avg_y < self.line_height and cy > self.line_height:
            self.process_enter_event(obj_id)

        # Person is exiting the bus
        elif avg_y > self.line_height and cy < self.line_height:
            self.process_exit_event(obj_id)
        return

    def process_enter_event(self, obj_id: int) -> None:
        # If person has already been moving in (down), do nothing
        if self.last_directions.get(obj_id) == 'down':
            return
        # Otherwise increment counter and write logs
        self.manager.count_in.value += 1
        self.last_directions[obj_id] = 'down'
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
        # If person has already been moving out (up), do nothing
        if self.last_directions.get(obj_id) == 'up':
            return
        # Otherwise increment counter and write logs
        self.manager.count_out.value += 1
        self.last_directions[obj_id] = 'up'
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
        extra_coords = len(self.previous_y_coords) - self.max_tracked_objects
        extra_dirs = len(self.last_directions) - self.max_tracked_objects
        if extra_coords > 0:
            for center in list(self.previous_y_coords.keys())[:extra_coords]:
                self.previous_y_coords.pop(center)
        if extra_dirs > 0:
            for obj_id in list(self.last_directions.keys())[:extra_dirs]:
                self.last_directions.pop(obj_id)
        return

    def track(self, *args, **kwargs) -> None:
        return self.update_counters(*args, **kwargs)

    def run(self, *args, **kwargs) -> None:
        return self.update_counters(*args, **kwargs)

    def __call__(self, *args, **kwargs) ->  None:
        return self.update_counters(*args, **kwargs)
