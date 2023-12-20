import os

from ultralytics import YOLO


if __name__ == "__main__":
    paths = [
        # "../base_models/yolov8s-cls.pt",
        # "../models/model_2023-12-14s.pt",
        "../base_models/yolov8s.pt",
        # "../base_models/yolov8m.pt",
        # "../base_models/yolov8n.pt",
        # "../base_models/yolov8l.pt",
    ]
    for path in paths:
        model = YOLO(path)
        model.train(data='data.yaml', epochs=300, cos_lr=True)