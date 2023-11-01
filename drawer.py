from typing import Tuple

import cv2
import numpy as np

from iec_mgt_typing import StreamManager


class Drawer:

    def __init__(
        self, 
        manager: StreamManager,
        *,
        box_color: Tuple[int]=(255,0,255),
        box_thickness: int=2,
        font: int=cv2.FONT_HERSHEY_PLAIN,
        text_scale: float=1.5,
        in_origin: Tuple[int]=(20, 80),
        out_origin: Tuple[int]=(20, 110),
        in_color: Tuple[int]=(0, 255, 0),
        out_color: Tuple[int]=(0, 0, 255),
        text_thickness: int=2,
        line_color: Tuple[int]=(0,0,255),
        line_thickness: int=5,
        ):
        self.manager = manager
        self.box_color = box_color
        self.box_thickness = box_thickness
        self.font = font
        self.text_scale = text_scale
        self.in_origin = in_origin
        self.out_origin = out_origin
        self.in_color = in_color
        self.out_color = out_color
        self.text_thickness = text_thickness
        self.line_color = line_color
        self.line_thickness = line_thickness
        return

    def draw_boxes(self, frame: np.ndarray) -> np.ndarray:
        for box in self.manager.boxes:
            x1, y1, x2, y2 = map(int, box)
            print(x1, y1, x2, y2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.box_color, self.box_thickness)
        return frame

    def draw_line(self, frame: np.ndarray) -> np.ndarray:
        cv2.line(
            frame, 
            (self.manager.enter_line[0], self.manager.enter_line[1]), 
            (self.manager.enter_line[2], self.manager.enter_line[3]), 
            self.line_color,
            self.line_thickness
        )
        return frame

    def put_in_out_data(self, frame: np.ndarray) -> np.ndarray:
        cv2.putText(
            frame, 
            f'People In: {self.manager.count_in}',
            self.in_origin, 
            self.font,
            self.text_scale,
            self.in_color,
            self.text_thickness
        )
        cv2.putText(
            frame,
            f'People Out: {self.manager.count_out}',
            self.out_origin,
            self.font,
            self.text_scale,
            self.out_color,
            self.text_thickness
        )
        return frame

    def imshow(self, name: str, frame: np.ndarray) -> None:
        frame = self.draw_line(frame)
        frame = self.draw_boxes(frame)
        frame = self.put_in_out_data(frame)
        cv2.imshow(name, frame)
        return

    def run(self, name: str, frame: np.ndarray) -> None:
        return self.imshow(name, frame)

    def __call__(self, name: str, frame: np.ndarray) -> None:
        return self.imshow(name, frame)