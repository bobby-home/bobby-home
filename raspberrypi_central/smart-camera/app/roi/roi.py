import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple

from camera.camera_analyze import Consideration


class ROI(ABC):
    def __init__(self, consideration: Consideration):
        self.consideration = consideration

    @abstractmethod
    def get_contours(self) -> Tuple[np.ndarray, Tuple[float, float]]:
        pass


class RectangleROI(ROI):
    def __init__(self, consideration: Consideration, x: float, y: float, w: float, h: float, definition_width: float, definition_height: float):
        self.definition_width = definition_width
        self.definition_height = definition_height
        self.y = y
        self.x = x
        self.w = w
        self.h = h
        super().__init__(consideration)

    def __eq__(self, other):
        if not isinstance(other, RectangleROI):
            return NotImplemented

        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h and self.definition_width == other.definition_width and self.definition_height == other.definition_height

    def get_contours(self):
        x1, y1 = (self.x, self.y + self.h)
        x2, y2 = (self.x + self.w, self.y + self.h)
        x3, y3 = (self.x + self.w, self.y)
        x4, y4 = (self.x, self.y)

        points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])

        return points.reshape((-1, 1, 2)).astype(np.int32), (self.definition_width, self.definition_height)
