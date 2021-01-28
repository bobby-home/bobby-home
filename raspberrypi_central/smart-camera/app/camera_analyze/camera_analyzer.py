from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from object_detection.model import BoundingBox


@dataclass
class Consideration:
    type: str
    id: Optional[int] = None


class CameraAnalyzer(metaclass=ABCMeta):
    @abstractmethod
    def considered_objects(self, object_bounding_box: BoundingBox) -> List[Consideration]:
        pass

    @abstractmethod
    def __eq__(self, other):
        pass
