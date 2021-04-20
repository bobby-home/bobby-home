from typing import List

from alarm.use_cases.out_alarm import notify_alarm_status_factory
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetected
from devices.models import Device

def alarm_status_changed(alarm_status: AlarmStatus, force=False):
    """
    Call this method when you changed an instance of alarm status.
    Used to communicate with services, to sync status.

    Parameters
    ----------
    alarm_status : AlarmStatus
        The instance that has been modified.
    force : bool
        If it's true, it forces the synchronization.
    """
    notify_alarm_status_factory().publish_status_changed(alarm_status.device_id, alarm_status, force)


def alarm_statuses_changed(alarm_statuses: List[AlarmStatus], force=False):
    """
    Call this method when you changed a list of alarm status.
    Used to communicate with services, to sync status.

    Parameters
    ----------
    alarm_statuses : List[AlarmStatus]
    force : bool
        If it's true, it forces the synchronization.
    """
    for alarm_status in alarm_statuses:
        alarm_status_changed(alarm_status, force)


def can_turn_off(device: Device) -> bool:
    """
    If a motion is being detected you cannot turn off the alarm on the device.
    Otherwise, it would be a huge flaw: a schedule could turn off the alarm even if somebody is being detected.
    Note: the system allows the the resident to force the turn off.

    Parameters
    ----------
    device : Device
        The device that host the alarm service.

    Returns
    -------
    bool
        Whether or not the alarm can be turned off for the given device.
    """
    try:
        motion = CameraMotionDetected.objects.filter(device=device, closed_by_system=False).latest('motion_started_at')
    except CameraMotionDetected.DoesNotExist:
        return True

    return motion.motion_ended_at is not None
