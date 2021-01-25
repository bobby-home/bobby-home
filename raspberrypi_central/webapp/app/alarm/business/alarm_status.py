from typing import List

from alarm.communication.out_alarm import notify_alarm_status_factory
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetected
from devices.models import Device

def alarm_status_changed(alarm_status: AlarmStatus, force=False):
    notify_alarm_status_factory().publish_status_changed(alarm_status.device_id, alarm_status.running)


def alarm_statuses_changed(alarm_statuses: List[AlarmStatus], force=False):
    for alarm_status in alarm_statuses:
        alarm_status_changed(alarm_status, force)


def can_turn_off(device: Device) -> bool:
    try:
        motion = CameraMotionDetected.objects.filter(device=device, closed_by_system=False).latest('motion_started_at')
    except CameraMotionDetected.DoesNotExist:
        return True

    return motion.motion_ended_at is not None
