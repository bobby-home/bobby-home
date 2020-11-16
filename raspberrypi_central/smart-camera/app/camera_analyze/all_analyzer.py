from typing import List

from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration
from object_detection.model import BoundingBox


class NoAnalyzer(CameraAnalyzer):

    def __init__(self, consideration: Consideration):
        self._consideration = consideration

    def __eq__(self, other):
        if not isinstance(other, NoAnalyzer):
            return NotImplemented

        return True

    def considered_objects(self, object_bounding_box: BoundingBox) -> List[Consideration]:
        return [self._consideration]
