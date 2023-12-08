import math
import time
from typing import Tuple

import cv2
import numpy as np
from ultralytics import YOLO

from sort import Sort


def make_output_path() -> str:
    return  f"output_video{int(time.time())%1000}.mp4"


def main(**kwargs) -> Tuple[int, int]:
    # Get parameters
    stream = kwargs.pop("stream", None)
    weights = kwargs.pop("weights", None)
    output_path = kwargs.pop("output_path", None)
    width = kwargs.pop("width", 640)
    height = kwargs.pop("height", 640)
    video_shape = (width, height)
    detect_conf = kwargs.pop("detect_conf", 0.3)
    detect_iou = kwargs.pop("detect_iou", 0.1)
    tracker_max_age = kwargs.pop("tracker_max_age", 120)
    tracker_min_hits = kwargs.pop("tracker_min_hits", 1)
    tracker_iou = kwargs.pop("tracker_iou", 0.1)
    fourcc_str = kwargs.pop("fourcc_str", "XVID")
    fps = kwargs.pop("fps", 30)

    # Check if parameters are valid
    if not stream:
        raise ValueError("No stream to process")
    if not weights:
        raise ValueError(
            """
            No path to model weights provided. 
            Check out, that 'weights' keyword argument is not None.
            """
        )

    # Initialize workers
    cap = cv2.VideoCapture(stream)  # For Video
    model = YOLO(weights)
    tracker = Sort(
        max_age=tracker_max_age,
        min_hits=tracker_min_hits,
        iou_threshold=tracker_iou,
    )
    if output_path is not None:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        writer = cv2.VideoWriter(output_path, fourcc, fps, video_shape)
    else:
        writer = None

    # Set up central line
    central_line = [0, 320, 640, 320]

    # Track previous y-coordinates of the center of bounding boxes
    last_direction = {}
    previous_y_coords = {}
    num_frames_to_average = 5

    # Counters for movement directions
    count_up = 0
    count_down = 0

    frame_counter = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        # frame_counter += 1
        # if frame_counter < 157 * fps:#1200:
        #     continue
        # if frame_counter > 174 * fps:#1600
        #     break

        img = cv2.resize(img, video_shape)
        results = model(img, stream=True, conf=detect_conf, iou=detect_iou)

        detections = np.empty((0, 5))

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])

                if cls == 0 and conf > 0.3:
                    # Drawing the bounding boxes
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    currentArray = np.array([x1, y1, x2, y2, conf])
                    detections = np.vstack((detections, currentArray))

        resultsTracker = tracker.update(detections)

        print(f"RESULTS TRACKER: {resultsTracker}")

        # Draw the central line
        cv2.line(img, (central_line[0], central_line[1]), (central_line[2], central_line[3]), (0, 0, 255), 5)

        for result in resultsTracker:
            x1, y1, x2, y2, id = result
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            
            # Store the last few y-coordinates
            if id not in previous_y_coords:
                previous_y_coords[id] = []
            previous_y_coords[id].append(cy)
            if len(previous_y_coords[id]) > num_frames_to_average:
                previous_y_coords[id].pop(0)

            avg_previous_y = sum(previous_y_coords[id]) / len(previous_y_coords[id])

            # Check direction of movement when crossing the central line
            if avg_previous_y < central_line[1] and cy > central_line[1]:
                if last_direction.get(id) != 'down':
                    count_down += 1
                    last_direction[id] = 'down'
            elif avg_previous_y > central_line[1] and cy < central_line[1]:
                if last_direction.get(id) != 'up':
                    count_up += 1
                    last_direction[id] = 'up'
            cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,255), 2)

            cv2.circle(img, ((x1+x2)//2, int(avg_previous_y)), 5, (255,0,0), -1)

            # Visualization
            cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            cv2.putText(img, f'ID: {int(id)}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        # Display counts
        cv2.putText(img, f'People In: {count_down}', (20, 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f'People Out: {count_up}', (20, 110), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)

        cv2.imshow("Image", img)
        k = cv2.waitKey(20)
        if k == ord("q"):
            time.sleep(1)
            break
        if writer:
            writer.write(img)

    # Close the video window
    cv2.destroyAllWindows()
    cap.release()
    if writer:
        writer.release()
    return (count_down, count_down)


if __name__ == "__main__":
    # Parameters' definitions
    # stream = "video_2023-11-25_hour20_cam1.mp4"
    stream = "video_2023-11-25_hour20_cam2.mp4"
    # stream = "video_2023-11-25_hour20_cam3.mp4"
    weights = "models/model_2023-12-04.pt"
    # weights = "../modules/model.pt"
    # output_path = make_output_path()
    # output_path = None
    output_path = f"output_video.mp4"
    width = 640
    height = 640
    detect_conf = 0.3
    detect_iou = 0.1
    tracker_max_age = 120
    tracker_min_hits = 1
    tracker_iou = 0.1
    fourcc_str = "XVID"
    fps = 30

    kwargs = {
        "stream": stream,
        "weights": weights,
        "output_path": output_path,
        "width": width,
        "height": height,
        "detect_conf": detect_conf,
        "detect_iou": detect_iou,
        "tracker_max_age": tracker_max_age,
        "tracker_min_hits": tracker_min_hits,
        "tracker_iou": tracker_iou,
        "fourcc_str": fourcc_str,
        "fps": fps

    }

    main(**kwargs)