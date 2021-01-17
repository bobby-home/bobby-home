import os
import logging
from pathlib import Path
from typing import List

from celery import shared_task
from camera.models import CameraMotionDetectedPicture
from devices.models import Device, SeverityChoice
from notification.tasks import send_picture, send_video, create_and_send_notification
from utils.mqtt import mqtt_factory
from alarm.communication.in_motion import save_motion
from .messaging import speaker_messaging_factory
from alarm.models import AlarmSchedule, AlarmStatus


LOGGER = logging.getLogger(__name__)

def h264_to_mp4(input_path, output_path = None) -> str:
    if output_path is None:
        path, ext = os.path.splitext(input_path)
        output_path = path + ".mp4"

    # MP4Box redirect everything to stderr (even if no error).
    # so we redirect stderr to stdout to /dev/null
    # so nothing is printed to avoid logs pollution.
    # if an error happens, we catch it thanks to the result.
    command = f'MP4Box -add {input_path} {output_path} > /dev/null 2>&1'

    # warning: call could be problematic in Celery tasks.
    result = os.system(command)
    if result != 0:
        raise Exception(f'{command} did not exited successfully.')

    return output_path

@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5},
    default_retry_delay=3)
def process_video(video_path: str):
    video_path = f'/usr/src/{video_path}'

    if not Path(video_path).is_file():
        raise FileNotFoundError(f'{video_path} does not exist.')

    output_path = h264_to_mp4(video_path)
    LOGGER.info(f'video to mp4 ok - {output_path}')

    kwargs = {
        'video_path': output_path
    }

    send_video.apply_async(kwargs=kwargs)


@shared_task(name="security.play_sound")
def play_sound(device_id: str):
    # device = device_models.Device.objects.get(device_id=device_id)
    mqtt_client = mqtt_factory()

    speaker = speaker_messaging_factory(mqtt_client)
    speaker.publish_speaker_status(device_id, True)


@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(device_id: str, picture_path: str, event_ref: str, status: str):
    device = Device.objects.get(device_id=device_id)

    picture = CameraMotionDetectedPicture(device=device, event_ref=event_ref, is_motion=status)

    """
    Warning: hacky thing...
    - We need to set the file to the Django ImageField. Remember that the file is already saved on disk and picture_path
    represent the absolute path. For instance: /usr/src/app/media/1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg
    - But we cannot set picture.path directly, Django blocks this action. We only can change the picture.name which is the filename with extension.
        - To retrieve this, we use the os.path.basename which gives us what django accepts: "1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg".
    """
    picture.picture.name = os.path.basename(picture_path)
    picture.save()

    kwargs = {
        'picture_path': picture_path
    }

    send_picture.apply_async(kwargs=kwargs)


@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str, seen_in: dict, event_ref: str, status: bool):
    device, motion = save_motion(device_id, seen_in, event_ref, status)

    if device is None:
        # the motion is already save in db, and so the notification should have been already send.
        return None

    location = device.location

    if motion.is_motion:
        message = f'Une présence étrangère a été détectée chez vous depuis {device_id} {location.structure} {location.sub_structure}'
    else:
        message = f"La présence étrangère précédemment détectée chez vous depuis {device_id} {location.structure} {location.sub_structure} ne l'est plus."

    kwargs = {
        'severity': SeverityChoice.HIGH,
        'device_id': device_id,
        'message': message
    }

    """
    TODO: check if this is a correct way to create & run multiple jobs.
    ! They are not related, they have to run in total parallel.
    
    send_message can run multiple time for one notification See issue #94
    If something goes wrong in this function after the real send notification, then
    it will retry it -> notify the user multiple times.
    """
    create_and_send_notification.apply_async(kwargs=kwargs)

    # We do it in this task for now.
    # play_sound.apply_async(kwargs={'device_id': device_id})
    mqtt_client = mqtt_factory()
    speaker = speaker_messaging_factory(mqtt_client)
    speaker.publish_speaker_status(device_id, motion.is_motion)


def set_alarm_status(alarm_status_uui: str, status: bool):
    schedule = AlarmSchedule.objects.get(uuid=alarm_status_uui)

    alarm_statuses: List[AlarmStatus] = schedule.alarm_statuses.all()

    for alarm_status in alarm_statuses:
        alarm_status.running = status
        alarm_status.save()


@shared_task(name="alarm.set_alarm_off")
def set_alarm_off(alarm_status_uui):
    set_alarm_status(alarm_status_uui, False)


@shared_task(name="alarm.set_alarm_on")
def set_alarm_on(alarm_status_uui):
    set_alarm_status(alarm_status_uui, True)

