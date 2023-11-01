from kalman import KalmanFilter
import numpy as np
import scipy
from scipy.spatial.distance import cdist
from scipy.spatial import distance as dist


class CentroidTracker:
    def __init__(self, max_disappeared=50):
        self.next_object_id = 0
        self.objects = {}
        self.disappeared = {}
        self.direction = {}
        self.in_counted = {}
        self.out_counted = {}
        self.max_disappeared = max_disappeared

    def register(self, centroid):
        self.objects[self.next_object_id] = KalmanFilter(centroid[0], centroid[1])
        self.disappeared[self.next_object_id] = 0
        self.direction[self.next_object_id] = 0
        self.in_counted[self.next_object_id] = False
        self.out_counted[self.next_object_id] = False
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.direction[object_id]
        del self.in_counted[object_id]
        del self.out_counted[object_id]

    def update(self, centroids):
        if len(centroids) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.array(centroids, dtype="float")

        if len(self.objects) == 0:
            for i in range(len(centroids)):
                self.register(centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = np.array([kf.x[:2] for kf in self.objects.values()])
            object_centroids = object_centroids.reshape(-1, 2)

            distance = dist.cdist(object_centroids, input_centroids)

            rows = distance.min(axis=1).argsort()
            cols = distance.argmin(axis=1)[rows]

            used_rows = set()  # Define used_rows here
            used_cols = set()  # Define used_cols here

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                object_id = object_ids[row]
                initial_x, initial_y = input_centroids[col][0], input_centroids[col][1]
                kf = KalmanFilter(initial_x=initial_x, initial_y=initial_y)
                kf.predict()
                kf.correct(x=input_centroids[col][0], y=input_centroids[col][1])
                self.objects[object_id] = kf
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, distance.shape[0])).difference(used_rows)
            unused_cols = set(range(0, distance.shape[1])).difference(used_cols)

            if distance.shape[0] >= distance.shape[1]:
                for row in unused_rows:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_cols:
                    self.register(input_centroids[col])

        return self.objects