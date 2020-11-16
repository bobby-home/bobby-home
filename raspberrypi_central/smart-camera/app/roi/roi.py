from abc import ABC

from camera_analyze.camera_analyzer import Consideration
from object_detection.model import BoundingBox


class ROI(ABC):
    def __init__(self, consideration: Consideration):
        self.consideration = consideration


class RectangleROI(ROI):
    def __init__(self, consideration: Consideration, bounding_box: BoundingBox):
        self.bounding_box = bounding_box

        super().__init__(consideration)

    def __eq__(self, other):
        if not isinstance(other, RectangleROI):
            return NotImplemented

        return self.bounding_box == other.bounding_box
