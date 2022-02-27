from django.utils import timezone
from alarm.use_cases.data import Detection, InMotionVideoData
from typing import Sequence

from django.db import IntegrityError
from django.utils import timezone
from django.db.models.functions import Greatest

from camera.models import CameraMotionDetectedBoundingBox, CameraMotionDetected, CameraMotionVideo
from devices import models as device_models


def save_motion(device: device_models.Device, detections: Sequence[Detection], event_ref: str, status: bool) -> bool:
    if status is True:
        try:
            motion = CameraMotionDetected.objects.create(
                device=device,
                event_ref=event_ref,
                motion_started_at=timezone.now()
            )
            motion.save()
        except IntegrityError:
            # motion already saved, don't do anything.
            return False
    else:
        motion = CameraMotionDetected.objects.get(event_ref=event_ref, device=device)
        motion.motion_ended_at = timezone.now()
        motion.save()

    bounding_boxes = [CameraMotionDetectedBoundingBox(
        x=d.x, y=d.y, w=d.w, h=d.h,
        score=d.score, camera_motion_detected=motion
        ) for d in detections]

    CameraMotionDetectedBoundingBox.objects.bulk_create(bounding_boxes)

    return True

def save_camera_video(data: InMotionVideoData) -> None:
    device = device_models.Device.objects.get(device_id=data.device_id)

    try:
        CameraMotionVideo.objects.create(device=device, event_ref=data.event_ref, last_record=timezone.now())
    except IntegrityError:
        """
        That means that we received a record number that is already taken in account.
        - "Hey, I got the record nb. 3", "Ok, but I already got record nb 4 so it's fine".
        """
        CameraMotionVideo.objects.filter(device=device, event_ref=data.event_ref)\
            .update(number_records=Greatest('number_records', data.video_split_number+1))

