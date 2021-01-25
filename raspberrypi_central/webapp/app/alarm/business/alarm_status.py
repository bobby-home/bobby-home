from camera.models import CameraMotionDetected
from devices.models import Device


def can_turn_off(device: Device) -> bool:
    try:
        motion = CameraMotionDetected.objects.filter(device=device, closed_by_system=False).latest('motion_started_at')
    except CameraMotionDetected.DoesNotExist:
        return True

    return motion.motion_ended_at is not None
