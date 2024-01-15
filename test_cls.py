from collections import deque

import cv2
import numpy as np
tmp = np.zeros((1,1))
cv2.imshow("tmp", tmp)
cv2.waitKey(1)
cv2.destroyAllWindows()
from ultralytics import YOLO


model = YOLO('models/classify/cls-s_2023-12-30.pt')
# You can try these aggregation functions:
# - min
# - max
# - mean
# - other
# You can also try these sliding windows ('maxlen' param)
# - 3
# - 5
# - 10
# - 15
# - 20
# You can also vary 'threshold' param and test the performance.
# Currently the best results are achieved with: 
# - Aggregator: min
# - Threshold: 0.25
# - Maxlen: 10


def mean(lst: list) -> float:
    return sum(lst)/len(lst)


def door_state(
    left_door: np.ndarray,
    right_door: np.ndarray,
    left_data: deque,
    right_data: deque,
    threshold: float = 0.25
) -> str:
    left_results = model(left_door)
    right_results = model(right_door)

    left_data.append(left_results[0].probs.data[0])
    right_data.append(right_results[0].probs.data[0])

    # if left_results[0].probs.data[0] > threshold:#left_results[0].probs.data[1]:
    if min(left_data) > threshold:
        left_door_state = 'Closed'
    else:
        left_door_state = 'Open'

    # if right_results[0].probs.data[0] > threshold:#right_results[0].probs.data[1]:
    if min(right_data) > threshold:
        right_door_state = 'Closed'
    else:
        right_door_state = 'Open'

    print(min(left_data), min(right_data))

    if left_door_state == 'Open' and right_door_state == 'Open':
        return 'Open'
    else:
        return 'Closed'


def process_video(
    video_path: str,
    out_path: str = "out_cls.mp4",
    maxlen: int = 10
) -> None:
    cap = cv2.VideoCapture(video_path)
    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"MP4V"), 30, (640,640))
    left_data = deque(maxlen=maxlen)
    right_data = deque(maxlen=maxlen)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        third_width = width // 3
        left_door = frame[:, :third_width]
        right_door = frame[:, -third_width:]

        result = door_state(left_door, right_door, left_data, right_data)

        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (500, 50)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2

        cv2.putText(frame, result, 
                    bottomLeftCornerOfText, 
                    font, 
                    fontScale,
                    fontColor,
                    lineType)

        writer.write(frame)
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    writer.release()
    return

if __name__ == "__main__":
    streams = [
        # "video_2023-11-20_hour17_cam1.mp4",
        "video_2023-11-20_hour17_cam2.mp4",
        "video_2023-11-20_hour17_cam3.mp4",
    ]
    for i, stream in enumerate(streams, 2):
        print(stream)
        process_video(stream, f"out_{i}.mp4")