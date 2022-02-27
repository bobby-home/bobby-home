from camera.models import CameraMotionDetected
from devices.models import Device


def current_motions():
    return CameraMotionDetected.objects.filter(closed_by_system=False, motion_ended_at__isnull=True)

def current_motions_device(device: Device):
    return CameraMotionDetected.objects.filter(closed_by_system=False, motion_ended_at__isnull=True, device=device)

