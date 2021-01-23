import os
import logging
from pathlib import Path
from typing import List

from celery import shared_task
from notification.tasks import send_video
from .business.camera_motion import camera_motion_factory
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


@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(device_id: str, picture_path: str, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_picture(device_id, picture_path, event_ref, status)

@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str, seen_in: dict, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_detected(device_id, seen_in, event_ref, status)


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
