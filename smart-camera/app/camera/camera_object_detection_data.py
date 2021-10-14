from dataclasses import dataclass


@dataclass(frozen=True)
class CameraObjectDetectionData:
    deplay_to_trigger_motion: int
    deplay_to_trigger_no_motion: int

