from typing import List, Dict

from django.db import IntegrityError

from alarm.models import CameraMotionDetected
from alarm.models.camera import CameraMotionDetectedBoundingBox
from devices import models as device_models


def save_motion(device_id: str, seen_in: Dict[str, Dict[str, any]], event_ref: str, status: bool):
    device = device_models.Device.objects.get(device_id=device_id)

    try:
        motion = CameraMotionDetected.objects.create(device=device, event_ref=event_ref, is_motion=status)
        motion.save()
    except IntegrityError:
        return None, None

    if 'rectangle' in seen_in:
        seen_in_rectangle = seen_in['rectangle']

        rectangle_roi_id: List[str] = seen_in_rectangle['ids']
        motion.in_rectangle_roi.add(*rectangle_roi_id)

        bounding_box = seen_in_rectangle['bounding_box']

        CameraMotionDetectedBoundingBox.objects.create(**bounding_box, camera_motion_detected=motion).save()

    """
    TODO: save CameraMotionDetectedBoundingBox when we do not have ROI defined.
    1. when we don't have any roi defined how the consideration is created? I mean the "type" name, it's something like "any" or "all"
    where is it created? Smart-camera or here? because I need this value here.
    """

    return device, motion
