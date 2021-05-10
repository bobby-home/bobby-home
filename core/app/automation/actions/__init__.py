
from enum import Enum


class Triggers(Enum):
    ON_MOTION_DETECTED = 'on_motion_detected'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
