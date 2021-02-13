import os
import logging
from pathlib import Path
from typing import List

from celery import shared_task
from notification.tasks import send_video
from .business.alarm_schedule_change_status import AlarmScheduleChangeStatus
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
def process_video(video_file: str):
    videos = os.environ['VIDEO_FOLDER']

    video_path = os.path.join(videos, video_file)

    if not Path(video_path).is_file():
        raise FileNotFoundError(f'{video_path} does not exist.')

    output_path = h264_to_mp4(video_path)
    LOGGER.info(f'video to mp4 ok - {output_path}')

    kwargs = {
        'video_path': output_path
    }

    send_video.apply_async(kwargs=kwargs)


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5},
    default_retry_delay=3)
def retrieve_and_process_video(device_id: str, video_file: str):
    remote_path = f'/var/lib/camera/media/{video_file}'
    dest_path = os.environ['VIDEO_FOLDER']

    video_dest_path = os.path.join(dest_path, video_file)

    command = f"rsync -avt --remove-source-files pi@{device_id}:{remote_path} {video_dest_path}"
    os.system(command)

    process_video(video_dest_path)


@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(device_id: str, picture_path: str, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_picture(device_id, picture_path, event_ref, status)

@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str, seen_in: dict, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_detected(device_id, seen_in, event_ref, status)


@shared_task(name="alarm.set_alarm_off")
def set_alarm_off(alarm_status_uui):
    AlarmScheduleChangeStatus().turn_off(alarm_status_uui)


@shared_task(name="alarm.set_alarm_on")
def set_alarm_on(alarm_status_uui):
    AlarmScheduleChangeStatus().turn_on(alarm_status_uui)
