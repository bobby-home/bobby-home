from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
import numpy as np
from camera.detect_motion import ObjectBoundingBox


@dataclass
class Consideration:
    type: str
    id: Optional[int] = None


class CameraAnalyzeObject(metaclass=ABCMeta):
    @abstractmethod
    def is_object_considered(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox) -> List[Consideration]:
        pass
