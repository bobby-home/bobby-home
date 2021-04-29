from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class BoundingBox:
    """
    Definition given by Tensorflow.
    (ymin, xmin, ymax, xmax) rectangle to be drawn, where (ymin, xmin) and (ymax, xmax)
    are opposite corners of the desired rectangle.
    """
    ymin: float
    xmin: float
    ymax: float
    xmax: float

    def __post_init__(self):
        if self.ymin > self.ymax:
            raise ValueError(f'ymin ({self.ymin} has to be <= than ymax ({self.ymax}.')

        if self.xmin > self.xmax:
            raise ValueError(f'xmin ({self.xmin} has to be <= than xmax ({self.xmax}')

    def is_intersect(self, other) -> bool:
        if self.xmin > other.xmax or self.xmax < other.xmin:
            return False

        if self.ymin > other.ymax or self.ymax < other.ymin:
            return False

        return True

    @property
    def area(self):
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)


@dataclass
class BoundingBoxPointAndSize:
    """
    Data definition that will be send to the main system.
    It requires this format and not the Tensorflow format which is stored in BoundingBox
    """
    x: float
    y: float
    w: float
    h: float


@dataclass
class People:
    # These are absolute coordinates not relatives one processed by Tensorflow.
    # it has been rescaled for the image.
    bounding_box: BoundingBox

    bounding_box_point_and_size: BoundingBoxPointAndSize

    class_id: Any
    score: float

