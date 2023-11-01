from typing import List, Tuple

import numpy as np
import torch
from ultralytics import YOLO
import cv2


class Detector:
    def __init__(
        self,
        path: str,
        *,
        width: int=640,
        height: int=640,
        conf: float=0.3,
        device: str="cuda"
        ):
        """
        Initializes Detector instance:
        1. Loads model weights from the specified path.
        2. Sets image resize parameters: preferred width and height.
            Defaults: width = 640, height = 640
        3. Sends loaded model to specified device. 
            Default: 'cuda'
        """
        self.model = YOLO(path)
        self.device = device
        self.model.to(self.device)
        self.width = width
        self.height = width
        self.conf = conf
        return

    def preprocess(self, image: np.ndarray) -> torch.tensor:
        """
        Performs image preprocessing beforesending it to model for inference
        """
        # Resize the image in order to fit the model input shape
        resized_image = cv2.resize(image, (self.width, self.height))
        # Change axis order so that to fit model input shape:
        # (batch_size, n_channels, width, height)
        # As we send 1 image to model, it is assumed implicitly,
        # that batch_size = 1; so our first axis is 'n_channels'
        resized_image = resized_image.transpose(2, 0, 1)
        image_tensor = torch.from_numpy(resized_image).unsqueeze(0)
        # Send image to the same device, as the model.
        image_tensor = image_tensor.to(self.device)
        return image_tensor

    def process(self, image: np.ndarray) -> Tuple[List[Tuple[int,int,int,int]], List[int], List[float]]:
        """
        Performs inference and returns the following tuple:
        (boxes, classes, scores),
        where:
            boxes: List[Tuple[int, int, int, int]]: List of bounding box coordinates
                Each element of list is a tuple: (x1, y1, x2, y2).
                (x1, y1) - top left corner of the box.
                (x2, y2) - bottom right corner of the box.
                All coordinates are calculated in integers, according to image shape.
                Note: (0, 0) is considered as top left corner of the image.
            classes: List[int]: List of indexes of classes of detected objects.
            scores: List[float]: List of confidences of detected objects.
        """
        # Initialize storages
        boxes = []
        # Preprocess the image before processing it with NN
        image_tensor = self.preprocess(image)
        # Process image with NN
        with torch.no_grad():
            results = self.model(image_tensor, conf=self.conf)
        # Iterate over detected objects
        for result in results:
            boxes.append(result.boxes.xyxy)
            return boxes
        #     # Get Boxes object.
        #     boxes = result.boxes
        #     for box in boxes:
        #         # Get box coordinates as floats
        #         # x_i is in interval [0, self.width] 
        #         # y_i is in interval [0, self.height] 
        #         x1, y1, x2, y2 = box.xyxy[0]
        #         # Get image shape
        #         h, w, _ = image.shape
        #         # Calculate resize coefficients
        #         k1 = w / self.width
        #         k2 = h / self.height
        #         # Resize bounds according to input image shape
        #         x1, y1, x2, y2 = int(x1 * k1), int(y1 * k2), int(x2 * k1), int(y2 * k2)
        #         # Append bounds to output_boxes as tuple
        #         output_boxes.append((x1,y1,x2,y2))
        #         # Get class id
        #         cls_id = int(box.cls[0])
        #         # Append class id to 'classes' list
        #         classes.append(cls_id)
        #         # Get detection confidence
        #         score = box.conf[0]
        #         # Append confidence to list of scores
        #         scores.append(score)
        # return output_boxes, classes, scores