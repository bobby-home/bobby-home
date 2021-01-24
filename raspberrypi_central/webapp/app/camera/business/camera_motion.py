from django.db import transaction

from camera.models import CameraMotionDetected
from devices.models import Device


def close_unclosed_camera_motions(device_id: str):
    """
    Camera motion is opened and closed by mqtt events.
    - Opened: the field `motion_started_at` is defined but not `motion_ended_at`.
    - Closed: both fields are set.
    It might happen (in a bad scenario), that the close event does not happen (i.e service crash).
    This method close (thanks to the field `closed_by_system` turned to True) all unclosed motion for a given `device_id`.
    """
    device = Device.objects.get(device_id=device_id)

    no_closed_motions = CameraMotionDetected.objects.select_for_update().filter(device=device, motion_ended_at__isnull=True, closed_by_system=False)
    with transaction.atomic():
        for no_closed_motion in no_closed_motions:
            no_closed_motion.closed_by_system = True

        CameraMotionDetected.objects.bulk_update(no_closed_motions, ['closed_by_system'], batch_size=100)
