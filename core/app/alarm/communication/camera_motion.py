from alarm.mqtt.mqtt_data import InMotionCameraData, InMotionPictureData
import logging
import os
from django.db import transaction
import alarm.business.in_motion as in_motion
import notification.tasks as notification_tasks
from alarm.communication.out_alarm import notify_alarm_status_factory
from alarm.communication.play_sound import play_sound
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetectedPicture
from devices.models import Device
import alarm.notifications as alarm_notifications

LOGGER = logging.getLogger(__name__)

class CameraMotion:
    """
    Class with methods to react to camera motion events.
    Each method is executed in a corresponding Celery Task even if it's totally transparent here (and have to stay transparent!).
    """
    def __init__(self, save_motion, create_and_send_notification, send_picture, play_sound, notify_alarm_status_factory):
        self.save_motion = save_motion
        self.create_and_send_notification = create_and_send_notification
        self.send_picture = send_picture
        self.play_sound = play_sound
        self.notify_alarm_status_factory = notify_alarm_status_factory

    def camera_motion_picture(self, in_data: InMotionPictureData) -> None:
        device = Device.objects.get(device_id=in_data.device_id)

        """
        Warning: hacky thing...
        - We need to set the file to the Django ImageField. Remember that the file is already saved on disk and picture_path
        represent the absolute path. For instance: /usr/src/app/media/1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg
        - But we cannot set picture.path directly, Django blocks this action. We only can change the picture.name which is the filename with extension.
            - To retrieve this, we use the os.path.basename which gives us what django accepts: "1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg".
        """
        if in_data.status is True:
            picture = CameraMotionDetectedPicture(device=device, event_ref=in_data.event_ref)
            picture.motion_started_picture.name = os.path.basename(in_data.picture_path)
            picture.save()
        else:
            with transaction.atomic():
                picture = CameraMotionDetectedPicture.objects.select_for_update().get(device=device, event_ref=in_data.event_ref)
                picture.motion_ended_picture.name = os.path.basename(in_data.picture_path)
                picture.save()

        kwargs = {
            'picture_path': in_data.picture_path
        }

        self.send_picture.apply_async(kwargs=kwargs)

    def camera_motion_detected(self, data: InMotionCameraData) -> None:
        device, motion = self.save_motion(data.device_id, data.seen_in, data.event_ref, data.status)

        if device is None:
            # the motion is already save in db, and so the notification should have been already send.
            return None

        location = device.location

        if data.status is True:
            alarm_notifications.object_detected(device, location)
        else:
            alarm_notifications.object_no_more_detected(device, location)
            if AlarmStatus.objects.get(device=device).running is False:
                LOGGER.info(f'The alarm on device {device.device_id} did not turn off because a motion was here. Not here anymore, turning off.')
                # we need to turn off the service
                self.notify_alarm_status_factory().publish_status_changed(device.pk, False)

        self.play_sound(data.device_id, data.status)

def camera_motion_factory():
    return CameraMotion(in_motion.save_motion, notification_tasks.create_and_send_notification, notification_tasks.send_picture, play_sound, notify_alarm_status_factory)
