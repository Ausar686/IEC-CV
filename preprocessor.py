import numpy as np
import cv2

from iec_mgt_typing import StreamManager


class Preprocessor:

	def __init__(self, manager: StreamManager, width: int=640, height: int=640):
		self.width = width
		self.height = height
		self.manager = manager
		return

	def preprocess(self, frame: np.ndarray) -> np.ndarray:
		frame = cv2.resize(frame, (self.width, self.height))
		print(type(frame), frame.shape)
		return frame

	def run(self, frame: np.ndarray) -> np.ndarray:
		return self.preprocess(frame)

	def __call__(self, frame: np.ndarray) -> np.ndarray:
		return self.preprocess(frame)