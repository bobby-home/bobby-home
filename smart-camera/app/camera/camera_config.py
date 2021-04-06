from dataclasses import dataclass


@dataclass(frozen=True)
class CameraConfig:
    camera_width: int
    camera_height: int


camera_config = CameraConfig(640, 480)
