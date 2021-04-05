import os
from os import path
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
from .communication.camera_video import camera_video_factory
from .utils.video_processing import h264_to_mp4

LOGGER = logging.getLogger(__name__)

@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(device_id: str, picture_path: str, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_picture(device_id, picture_path, event_ref, status)

@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str, seen_in: dict, event_ref: str, status: bool):
    camera_motion_factory().camera_motion_detected(device_id, seen_in, event_ref, status)

@shared_task(name='security.camera_motion_video')
def camera_motion_video(device_id: str, video_ref: str) -> None:
    camera_video_factory().camera_video(device_id, video_ref)

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
