from typing import List, Dict

from django.db import IntegrityError

from alarm import models as alarm_models
from devices import models as device_models


def save_motion(device_id: str, seen_in: Dict[str, List[str]], event_ref: str):
    device = device_models.Device.objects.get(device_id=device_id)

    try:
        motion = alarm_models.CameraMotionDetected.objects.create(device=device, event_ref=event_ref)
        motion.save()
    except IntegrityError:
        return None

    if 'rectangle' in seen_in:
        rectangle_roi_id: List[str] = seen_in['rectangle']
        motion.in_rectangle_roi.add(*rectangle_roi_id)

    return device
