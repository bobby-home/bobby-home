import os
import logging
import re
from pathlib import Path
from typing import Optional, Tuple, List

from celery import shared_task, group, signature

from notification.consts import SeverityChoice
from notification.tasks import send_video, create_and_send_notification
from utils.date import is_time_newer_than
from .business import in_motion
from .business.alarm_change_status import AlarmScheduleChangeStatus
from alarm.communication.camera_motion import camera_motion_factory
from alarm.models import AlarmStatus, Ping
import alarm.notifications as notifications

LOGGER = logging.getLogger(__name__)

def h264_to_mp4(input_path: str, output_path: str):
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

    # MP4Box redirect everything to stderr (even if no error).
    # so we redirect stderr to stdout to /dev/null
    # so nothing is printed to avoid logs pollution.
    # if an error happens, we catch it thanks to the result.
    command = f'MP4Box -add {input_path} {output_path} > /dev/null 2>&1'

    # warning: call could be problematic in Celery tasks.
    result = os.system(command)
    if result != 0:
        raise Exception(f'{command} did not exited successfully.')


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5},
    default_retry_delay=3)
def process_video(raw_video_file: str, output_path: str) -> None:
    # videos = os.environ['VIDEO_FOLDER']
    #
    # raw_video_path = os.path.join(videos, raw_video_file)

    if not Path(raw_video_file).is_file():
        raise FileNotFoundError(f'{raw_video_file} does not exist.')

    h264_to_mp4(raw_video_file, output_path)
    LOGGER.info(f'video to mp4 ok - {output_path}')

    # we don't need raw h264 anymore.
    os.remove(raw_video_file)

    # kwargs = {
    #     'video_path': output_path
    # }
    #
    # send_video.apply_async(kwargs=kwargs)


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


@shared_task()
def merge_videos(videos_path: List[str], output_video_path: str) -> None:
    if len(videos_path) < 1:
        return None

    command_file = f'-add {videos_path[0]}'
    for video_path in videos_path[1:]:
        command_file += f' -cat {video_path}'

    command = f'MP4Box {command_file} {output_video_path} > /dev/null 2>&1'

    result = os.system(command)
    if result != 0:
        raise Exception(f'{command} did not exited successfully.')

@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(device_id: str, picture_path: str, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_picture(device_id, picture_path, event_ref, status)

@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str, seen_in: dict, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_detected(device_id, seen_in, event_ref, status)

@shared_task(name='security.camera_motion_video')
def camera_motion_video(device_id: str, video_ref: str, is_same_device: bool = False) -> None:
    """Save camera video reference to the database. It adds/extracts useful information.

     Parameters
     ----------
     device_id : str
        The device_id that sent the `video_ref`.

     video_ref : str
         A string that represents a video_ref, ex: '49efa0b4-2003-44e4-920c-4eb0e6eea358-1'
             composed by two parts: the first one, the `event_ref` and the `record_number`.

     is_same_device : bool
        Either or not the `device_id` (so the device) is the same as the one that executes the function.

     Returns
     -------
     None
     """


    """
    doing:
    if video ref is ending by "-0" we have to:
    - process the f'{video_ref}-before.h264' and the "-0", then merge them then send the notification.
    (process_video() & process_video()).then(merge).then(send)
    """

    videos_folder = os.environ['VIDEO_FOLDER']

    raw_video_file = os.path.join(videos_folder, f'{video_ref}.h264')
    video_file = os.path.join(videos_folder, f'{video_ref}.mp4')

    split_number_pattern = r"(?P<split_number>[0-9]+$)"
    split_number_re = re.search(split_number_pattern, video_ref)
    if split_number_re is None:
        raise ValueError(f'Wrong video_ref format: {video_ref}.')

    split_number = split_number_re.group()

    # first split, merge before video and splited video.
    if split_number == '0':
        print('first split, will merge before and current split video')

        video_ref_before_motion = f'{video_ref}-before'
        raw_video_file_before_motion = os.path.join(videos_folder, f'{video_ref_before_motion}.h264')
        raw_merged_video_file = os.path.join(videos_folder, f'{video_ref}-merged.h264')

        # job = group([
        #     process_video.s(raw_video_file),
        #     process_video.s(f'{video_file_before_motion}.h264')
        # ])
        # result = job.apply_async()
        # if not result.successful():
        #     raise Exception('not all subtasks were successful.')

        # process_video(raw_video_file, video_file)
        # process_video(f'{video_file_before_motion}.h264', f'{video_file_before_motion}.mp4')

        # output_path = f'{video_ref}.mp4'

        # -before -0 -> merged in raw_merged_video_file
        merge_videos([raw_video_file_before_motion, raw_video_file], raw_merged_video_file)

        # raw_merged_video_file to video_file mp4
        process_video(raw_merged_video_file, video_file)
        send_video(video_path=video_file)

    else:
        if is_same_device:
            # The system has some latency to save the video,
            # so we add a little countdown so the video will more likely be available after x seconds.
            process_video.apply_async(kwargs={'raw_video_file': raw_video_file})
        else:
            retrieve_and_process_video.apply_async(kwargs={'raw_video_file': raw_video_file, 'device_id': device_id})

    in_motion.save_camera_video(video_ref)

@shared_task(name="alarm.set_alarm_off")
def set_alarm_off(alarm_status_uui):
    AlarmScheduleChangeStatus().turn_off(alarm_status_uui)


@shared_task(name="alarm.set_alarm_on")
def set_alarm_on(alarm_status_uui):
    AlarmScheduleChangeStatus().turn_on(alarm_status_uui)


def check_ping(status: AlarmStatus) -> Tuple[bool, Ping]:
    try:
        ping = Ping.objects.get(device_id=status.device.device_id, service_name='object_detection')

        if ping.last_update is None:
            return False, ping

        return is_time_newer_than(ping.last_update, 60), ping
    except Ping.DoesNotExist:
        ping = Ping.objects.create(device_id=status.device.device_id, service_name='object_detection', last_update=None)
        return False, ping

class CheckPings:
    def __init__(self):
        pass

    def check(self):
        statuses = AlarmStatus.objects.filter(running=True)

        for status in statuses:
            result, ping = check_ping(status)
            device = status.device

            if result is False:
                ping.consecutive_failures += 1

                if ping.consecutive_failures == 3:
                    notifications.service_no_ping(status, ping)

                ping.save()
            elif ping.consecutive_failures >= 3:
                notifications.service_ping_back(status)

                ping.failures += ping.consecutive_failures
                ping.consecutive_failures = 0
                ping.save()

@shared_task()
def check_pings() -> None:
    CheckPings().check()
