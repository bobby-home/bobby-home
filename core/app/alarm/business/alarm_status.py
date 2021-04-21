from camera.models import CameraMotionDetected
from devices.models import Device


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
