from dataclasses import dataclass
from typing import Any, Optional, Sequence


@dataclass
class Detection:
    bounding_box: Any
    bounding_box_point_and_size: Any
    class_id: str
    score: float

@dataclass
class InMotionCameraData:
    device_id: str
    event_ref: str
    status: bool
    detections: Sequence[Detection]


@dataclass
class InMotionVideoData:
    device_id: str
    video_ref: str
    event_ref: str
    video_split_number: int


@dataclass
class InMotionPictureData:
    device_id: str
    picture_path: str
    event_ref: str
    status: bool

@dataclass
class DiscoverAlarmData:
    id: Any
    type: Optional[str] = None
    device_id: Optional[str] = None

