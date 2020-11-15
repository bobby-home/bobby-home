from typing import List

import numpy as np

from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration
from object_detection.model import ObjectBoundingBox


class NoAnalyzer(CameraAnalyzer):

    def __init__(self, consideration: Consideration):
        self._consideration = consideration

    def __eq__(self, other):
        return True

    def considered_objects(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox) -> List[Consideration]:
        return [self._consideration]
