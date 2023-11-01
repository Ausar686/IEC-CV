import numpy as np
import cv2


class KalmanFilter:
    def __init__(self, initial_x, initial_y):
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                              [0, 1, 0, 0]], dtype=np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                             [0, 1, 0, 1],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]], dtype=np.float32)

        # Adjust the process noise covariance matrix
        self.kf.processNoiseCov = 1e-3 * np.eye(4, dtype=np.float32)

        # Adjust the measurement noise covariance matrix
        self.kf.measurementNoiseCov = 1e-1 * np.eye(2, dtype=np.float32)

        # Adjust the error covariance matrix after correction
        self.kf.errorCovPost = 1e-1 * np.eye(4, dtype=np.float32)

        self.kf.statePost = np.array([[initial_x],
                                      [initial_y],
                                      [0],
                                      [0]], dtype=np.float32)
    def predict(self):
        self.kf.predict()

    def correct(self, x, y):
        measurement = np.array([[x], [y]], dtype=np.float32)
        self.kf.correct(measurement)

    @property
    def x(self):
        return self.kf.statePost