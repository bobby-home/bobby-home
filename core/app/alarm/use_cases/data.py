from dataclasses import dataclass
from typing import Optional


@dataclass
class InMotionCameraData:
    device_id: str
    event_ref: str
    status: bool
    seen_in: Optional[dict]


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

