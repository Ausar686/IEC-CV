from collections import deque
import time

from sort import Sort
from iec_mgt_typing import StreamManager
from log import Log, create_log


class Tracker:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (line_height, max_age, min_hits, iou_threshold, num_frames_to_average) = self.manager.tracker_tuple

        # Initialize tracker
        self.tracker = Sort(
            max_age=max_age,
            min_hits=min_hits,
            iou_threshold=iou_threshold
        )
        
        # Initialize line coordinates
        self.line_height = line_height

        # Initialize storages for tracking
        self.num_frames_to_average = num_frames_to_average
        self.last_directions = {}
        self.previous_y_coords = {}
        return


    def update_counters(self) -> None:
        # If there is no data to process, simply wait 
        if self.manager.detect_storage.empty():
            time.sleep(0.1)
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
                self.previous_y_coords[obj_id] = deque(maxlen=self.num_frames_to_average)
            self.previous_y_coords[obj_id].append(cy)

            # Calculate the average y-coordinate among recent frames
            avg_y = sum(self.previous_y_coords[obj_id]) / len(self.previous_y_coords[obj_id])

            # Update counters
            self.update_status_by_id(obj_id, cy, avg_y)    
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
        try:
            log = create_log(self.manager, "enter")
            self.manager.logs_storage.put(log)
        except Exception as e:
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
        try:
            log = create_log(self.manager, "exit")
            self.manager.logs_storage.put(log)
        except Exception as e:
            log = create_log(self.manager, "tracker_put_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return


    def track(self) -> None:
        return self.update_counters()


    def run(self) -> None:
        return self.update_counters()


    def __call__(self) ->  None:
        return self.update_counters()