import numpy as np

from camera.camera_analyze import CameraAnalyzeObject
from camera.detect_motion import ObjectBoundingBox


class NoAnalyzer(CameraAnalyzeObject):

    def is_object_considered(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox) -> bool:
        return True
