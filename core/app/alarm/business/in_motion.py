from alarm.mqtt.mqtt_data import InMotionVideoData
from typing import List, Dict

from django.db import IntegrityError
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest

from alarm.communication.alarm_consts import ROITypes
from camera.models import CameraMotionDetectedBoundingBox, CameraMotionDetected, CameraMotionVideo
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


def save_camera_video(data: InMotionVideoData) -> None:
    """Save camera video reference to the database. It add/extracts useful information.

    Parameters
    ----------
    video_ref : str
        A string that represents a video_ref, ex: '49efa0b4-2003-44e4-920c-4eb0e6eea358-1'
            composed by two parts: the first one, the `event_ref` and the `record_number`.

    Returns
    -------
    CameraMotionVideo
    """
    device = device_models.Device.objects.get(device_id=data.device_id)
    
    try:
        CameraMotionVideo.objects.create(device=device, event_ref=data.event_ref)
    except IntegrityError:
        """
        That means that we received a record number that is already taken in account.
        - "Hey, I got the record nb. 3", "Ok, but I already got record nb 4 so it's fine".
        """
        CameraMotionVideo.objects.filter(device=device, event_ref=data.event_ref)\
            .update(number_records=Greatest('number_records', data.video_split_number))

