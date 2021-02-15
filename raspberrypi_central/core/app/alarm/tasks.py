import os
import logging
from pathlib import Path
from typing import Optional, Tuple

from celery import shared_task

from notification.consts import SeverityChoice
from notification.tasks import send_video, create_and_send_notification
from utils.date import is_time_newer_than
from .business.alarm_schedule_change_status import AlarmScheduleChangeStatus
from .business.camera_motion import camera_motion_factory
from alarm.models import AlarmStatus, Ping


LOGGER = logging.getLogger(__name__)

def h264_to_mp4(input_path: str, output_path: Optional[str] = None) -> str:
    """Convert raw h264 'input_path' to mp4 in 'output_path' or in 'input_path' with .mp4 extension.

    Parameters
    ----------
    input_path : str
    output_path : str, optional

    Raises
    ------
    Exception
        If underlying MP4Box command is not exited normally,
            probably something went wrong and the file is not converted.

    Returns
    -------
    str
        The path to the newly (converted) video.
    """
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
def process_video(video_file: str) -> None:
    videos = os.environ['VIDEO_FOLDER']

    raw_video_path = os.path.join(videos, video_file)

    if not Path(raw_video_path).is_file():
        raise FileNotFoundError(f'{raw_video_path} does not exist.')

    output_path = h264_to_mp4(raw_video_path)
    LOGGER.info(f'video to mp4 ok - {output_path}')

    # we don't need raw h264 anymore.
    os.remove(raw_video_path)

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


def check_ping(status: AlarmStatus) -> Tuple[bool, Optional[Ping]]:
    try:
        ping = Ping.objects.get(device_id=status.device.device_id, service_name='object_detection')
        return is_time_newer_than(ping, 60), ping
        # ping.last_update.
    except Ping.DoesNotExist:
        return False, None


class CheckPings:
    def __init__(self):
        pass

    def check(self):
        statuses = AlarmStatus.objects.filter(running=True)

        for status in statuses:
            result, ping = check_ping(status)
            device = status.device

            if ping is None:
                msg = f'The service object_detection for the device {device} does not send any ping.'
                create_and_send_notification(severity=SeverityChoice.HIGH, device_id=status.device.device_id, message=msg)
                return None

            if result is False:
                ping.consecutive_failures += 1

                if ping.consecutive_failures > 3:
                    ping.failures += ping.consecutive_failures
                    ping.consecutive_failures = 0
                    msg = f'The service object_detection for the device {device} does not send any ping since {ping.last_update}.'
                    create_and_send_notification(severity=SeverityChoice.HIGH, device_id=status.device.device_id, message=msg)

                ping.save()
            elif ping.consecutive_failures > 0:
                msg = f'The service object_detection for the device {device} was not pinging but it does now. Everything is back to normal.'
                create_and_send_notification(severity=SeverityChoice.HIGH, device_id=status.device.device_id, message=msg)

                ping.failures += ping.consecutive_failures
                ping.consecutive_failures = 0
                ping.save()

@shared_task()
def check_pings() -> None:
    CheckPings().check()
