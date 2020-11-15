from typing import List

import numpy as np

from object_detection.model import ObjectBoundingBox
from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration


class ConsideredByAnyAnalyzer(CameraAnalyzer):
    def __init__(self, analyzers: List[CameraAnalyzer]):
        self._analyzers = analyzers

    def considered_objects(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox) -> List[Consideration]:
        for analyzer in self._analyzers:
            r = analyzer.considered_objects(frame, object_bounding_box)
            if len(r) > 0:
                return r

        return []

    def __eq__(self, other):
        if not isinstance(other, ConsideredByAnyAnalyzer):
            return NotImplemented

        return self._analyzers == other._analyzers
