from dataclasses import dataclass

import numpy as np


@dataclass
class BoundingBox:
    """
    Definition given by Tensorflow.
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
class ObjectBoundingBox(BoundingBox):
    contours: np.ndarray


@dataclass
class People:
    # These are absolute coordinates not relatives one processed by Tensorflow.
    # it has been rescaled for the image.
    bounding_box: ObjectBoundingBox
    bounding_box_point_and_size: BoundingBoxPointAndSize
    class_id: any
    score: float
