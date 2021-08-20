
from enum import Enum


class Triggers(Enum):
    ON_MOTION_DETECTED = 'on_motion_detected'
    ON_MOTION_LEFT = 'on_motion_left'
    ON_ALARM_OFF = 'on_alarm_off'
    ON_ALARM_ON = 'on_alarm_on'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
