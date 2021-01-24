from django.db import transaction

from camera.models import CameraMotionDetected
from devices.models import Device


def close_unclosed_camera_motions(device_id: str):
    device = Device.objects.get(device_id=device_id)

    no_closed_motions = CameraMotionDetected.objects.select_for_update().filter(device=device, motion_ended_at__isnull=True, closed_by_system=False)
    with transaction.atomic():
        for no_closed_motion in no_closed_motions:
            no_closed_motion.closed_by_system = True

        CameraMotionDetected.objects.bulk_update(no_closed_motions, ['closed_by_system'], batch_size=100)
