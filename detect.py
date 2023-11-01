import numpy as np
from ultralytics import YOLO
import torch

from iec_mgt_typing import StreamManager


class Detector:

	def __init__(self, weights: str, manager: StreamManager, conf: float=0.3):
		self.model = YOLO(weights)
		self.manager = manager
		self.conf = conf
		return

	def detect(self, frame: np.ndarray) -> np.ndarray:
		with torch.no_grad():
			results = self.model(frame, conf=self.conf)
		for r in results: # DO NOT pass several images to Detector at once
			detections = np.empty((0, 4))
			# Convert to numpy array of integers (to be able to draw bboxes)
			xyxy = r.boxes.xyxy.cpu().numpy()
			detections = np.vstack((detections, xyxy))
			self.manager.boxes = detections
			return detections

	def process(self, frame: np.ndarray) -> np.ndarray:
		return self.detect(frame)

	def run(self, frame: np.ndarray) -> np.ndarray:
		return self.detect(frame)

	def __call__(self, frame: np.ndarray) -> np.ndarray:
		return self.detect(frame)