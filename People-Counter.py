import numpy as np
from ultralytics import YOLO
import cv2
import pyresearch
import math
from sort import *

cap = cv2.VideoCapture("test3.mp4")  # For Video
model = YOLO("model.pt")

tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Set up central line
central_line = [0, 320, 640, 320]

# Track previous y-coordinates of the center of bounding boxes
last_direction = {}
previous_y_coords = {}
num_frames_to_average = 5

# Counters for movement directions
count_up = 0
count_down = 0

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.resize(img, (640, 640))
    results = model(img, stream=True)

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
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
                currentArray = np.array([x1, y1, x2, y2, conf])
                detections = np.vstack((detections, currentArray))

    resultsTracker = tracker.update(detections)

    # Draw the central line
    cv2.line(img, (central_line[0], central_line[1]), (central_line[2], central_line[3]), (0, 0, 255), 5)

    for result in resultsTracker:
        x1, y1, x2, y2, id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        cx, cy = x1 + w // 2, y1 + h // 2
        
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

        # Visualization
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        cv2.putText(img, f'ID: {int(id)}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # Display counts
    cv2.putText(img, f'People Out: {count_up}', (20, 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
    cv2.putText(img, f'People In: {count_down}', (20, 110), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

# Close the video window
cv2.destroyAllWindows()