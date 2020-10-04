from typing import List

from alarm import models as alarm_models
from devices import models as device_models


def save_motion(device_id, seen_in):
    device = device_models.Device.objects.get(device_id=device_id)

    rectangle_roi_id: List[str] = seen_in.get('rectangle')
    print(f'rectangle_roi_id={rectangle_roi_id}')
    motion = alarm_models.CameraMotionDetected(device=device)
    motion.save()

    motion.in_rectangle_roi.add(*rectangle_roi_id)


    return device
