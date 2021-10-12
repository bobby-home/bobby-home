from dataclasses import dataclass


@dataclass(frozen=True)
class CameraObjectDetectionData:
    seconds_lapsed_to_trigger_motion: int
    seconds_lapsed_to_trigger_no_motion: int

