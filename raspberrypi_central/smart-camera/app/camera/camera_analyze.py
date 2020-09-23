from abc import ABC, ABCMeta, abstractmethod
import numpy as np
from camera.detect_motion import ObjectBoundingBox


class CameraAnalyzeObject(metaclass=ABCMeta):
    @abstractmethod
    def is_object_considered(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox):
        pass
