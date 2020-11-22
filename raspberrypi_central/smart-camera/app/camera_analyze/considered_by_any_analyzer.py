from typing import List

import numpy as np

from object_detection.model import BoundingBoxWithContours, BoundingBox
from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration


class ConsideredByAnyAnalyzer(CameraAnalyzer):
    def __init__(self, analyzers: List[CameraAnalyzer]):
        self._analyzers = analyzers

    def considered_objects(self,  object_bounding_box: BoundingBox) -> List[Consideration]:
        for analyzer in self._analyzers:
            r = analyzer.considered_objects(object_bounding_box)
            if len(r) > 0:
                return r

        return []

    def __eq__(self, other):
        if not isinstance(other, ConsideredByAnyAnalyzer):
            return NotImplemented

        return self._analyzers == other._analyzers
