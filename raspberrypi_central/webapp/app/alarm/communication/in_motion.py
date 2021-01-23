from typing import List, Dict

from django.db import IntegrityError
from django.utils import timezone

from alarm.communication.alarm_consts import ROITypes
from camera.models import CameraMotionDetectedBoundingBox, CameraMotionDetected
from devices import models as device_models
from hello_django.loggers import LOGGER


def _save_bounding_box(data, motion: CameraMotionDetected):
    bounding_box = data['bounding_box']
    CameraMotionDetectedBoundingBox.objects.create(**bounding_box, camera_motion_detected=motion).save()


def save_motion(device_id: str, seen_in: Dict[str, Dict[str, any]], event_ref: str, status: bool):
    device = device_models.Device.objects.get(device_id=device_id)

    if status is True:
        try:
            motion = CameraMotionDetected.objects.create(device=device, event_ref=event_ref, motion_started_at=timezone.now())
            motion.save()
        except IntegrityError:
            return None, None
    else:
        motion = CameraMotionDetected.objects.get(event_ref=event_ref, device=device)
        motion.motion_ended_at = timezone.now()
        motion.save()

    if ROITypes.RECTANGLES.value in seen_in:
        seen_in_rectangle = seen_in[ROITypes.RECTANGLES.value]

        rectangle_roi_id: List[str] = seen_in_rectangle['ids']
        motion.in_rectangle_roi.add(*rectangle_roi_id)

        _save_bounding_box(seen_in_rectangle, motion)

    elif ROITypes.FULL.value in seen_in:
        full = seen_in[ROITypes.FULL.value]

        _save_bounding_box(full, motion)
    else:
        LOGGER.error(f'{seen_in} is not understandable by our system.')

    return device, motion
