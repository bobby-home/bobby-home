from typing import List, Dict

from django.db import IntegrityError

import alarm.models.camera
from alarm import models as alarm_models
from devices import models as device_models


def save_motion(device_id: str, seen_in: Dict[str, List[str]], event_ref: str, status: bool):
    device = device_models.Device.objects.get(device_id=device_id)

    try:
        motion = alarm.models.camera.CameraMotionDetected.objects.create(device=device, event_ref=event_ref, is_motion=status)
        motion.save()
    except IntegrityError:
        return None, None

    if 'rectangle' in seen_in:
        rectangle_roi_id: List[str] = seen_in['rectangle']
        motion.in_rectangle_roi.add(*rectangle_roi_id)

    return device, motion