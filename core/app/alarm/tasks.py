from alarm.use_cases.data import InMotionCameraData, InMotionPictureData, InMotionVideoData
import os
import logging
from typing import Tuple

from celery import shared_task
from utils.date import is_time_newer_than
from .business.alarm_change_status import AlarmScheduleChangeStatus
from alarm.models import AlarmStatus, Ping
import alarm.notifications as notifications
import alarm.use_cases.camera_picture as camera_picture
import alarm.use_cases.camera_motion as camera_motion
import alarm.use_cases.camera_video as camera_video


LOGGER = logging.getLogger(__name__)

@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(data: dict) -> None:
    in_data = InMotionPictureData(**data)
    camera_picture.camera_motion_picture(in_data)

@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(data: dict) -> None:
    in_data = InMotionCameraData(**data)
    camera_motion.camera_motion_detected(in_data)

@shared_task(name='security.camera_motion_video')
def camera_motion_video(data: dict) -> None:
    in_data = InMotionVideoData(**data)
    camera_video.camera_video_factory().camera_video(in_data)


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
