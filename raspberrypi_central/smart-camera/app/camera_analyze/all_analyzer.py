from typing import List

import numpy as np

from camera.camera_analyze import CameraAnalyzeObject, Consideration
from camera.detect_motion import ObjectBoundingBox


class NoAnalyzer(CameraAnalyzeObject):

    def __init__(self, consideration: Consideration):
        self._consideration = consideration

    def __eq__(self, other):
        return True

    def considered_objects(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox) -> List[Consideration]:
        return [self._consideration]
