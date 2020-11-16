from typing import List

from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration
from roi.roi import RectangleROI
from object_detection.model import BoundingBox


class CameraAnalyzerRectangleROI(CameraAnalyzer):
    def __init__(self, roi: RectangleROI):
        self._roi = roi

    def considered_objects(self, other_bounding_box: BoundingBox) -> List[Consideration]:
        if self._roi.bounding_box.is_intersect(other_bounding_box):
            return [self._roi.consideration]

        return []

    def __str__(self):
        return self._roi

    def __eq__(self, other):
        if not isinstance(other, CameraAnalyzerRectangleROI):
            return NotImplemented

        return self._roi == other._roi
