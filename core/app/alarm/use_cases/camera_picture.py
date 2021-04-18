import os
from django.db import transaction
from camera.models import CameraMotionDetectedPicture
from devices.models import Device
from alarm.mqtt.mqtt_data import InMotionPictureData
import notification.tasks as notification_tasks


def camera_motion_picture(in_data: InMotionPictureData) -> None:
    device = Device.objects.get(device_id=in_data.device_id)

    """
    Warning: hacky thing...
    - We need to set the file to the Django ImageField. Remember that the file is already saved on disk and picture_path
    represent the absolute path. For instance: /usr/src/app/media/1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg
    - But we cannot set picture.path directly,
        Django blocks this action. We only can change the picture.name which is the filename with extension.
    - To retrieve this, we use the os.path.basename which gives us what django accepts: "1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg".
    """
    if in_data.status is True:
        picture = CameraMotionDetectedPicture(device=device, event_ref=in_data.event_ref)
        picture.motion_started_picture.name = os.path.basename(in_data.picture_path)
        picture.save()
    else:
        updated: int = CameraMotionDetectedPicture.objects.filter(
            device=device,
            event_ref=in_data.event_ref,
            motion_ended_picture__exact='').update(motion_ended_picture = os.path.basename(in_data.picture_path))

        if updated == 0:
            raise ValueError(f'Motion ended picture for event {in_data.event_ref} on device {device} already registered or motion event does not exist.')

    kwargs = {
        'picture_path': in_data.picture_path
    }

    notification_tasks.send_picture.apply_async(kwargs=kwargs)


