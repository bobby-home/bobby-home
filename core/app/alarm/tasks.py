from alarm.use_cases.alarm_camera_video_manager import alarm_camera_video_manager_factory
from camera.models import CameraMotionDetected, CameraMotionVideo
from alarm.use_cases.camera_video import camera_video
from utils.mqtt import mqtt_factory
import uuid
from devices.models import Device, DeviceType
from alarm.use_cases.data import Detection, DiscoverAlarmData, InMotionCameraData, InMotionPictureData, InMotionVideoData
import alarm.use_cases.alarm_schedule_range as alarm_schedule_range
import logging
from typing import Tuple

from celery import shared_task
from utils.date import is_time_newer_than
from alarm.models import AlarmStatus, Ping
import alarm.notifications as notifications
import alarm.use_cases.camera_picture as camera_picture
import alarm.use_cases.camera_motion as camera_motion
import alarm.use_cases.alarm_discovery as alarm_discovery
from alarm.use_cases.alarm_status import AlarmScheduleChangeStatus


LOGGER = logging.getLogger(__name__)

@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(data: dict) -> None:
    in_data = InMotionPictureData(**data)
    camera_picture.camera_motion_picture(in_data)

@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(data: dict) -> None:
    detections_plain = data.get('detections', [])

    data['detections'] = [Detection(**d) for d in detections_plain]
    in_data = InMotionCameraData(**data)

    cm = camera_motion.camera_motion_factory()
    if in_data.status is True:
        cm.motion_detected(in_data)
    elif in_data.status is False:
        cm.motion_detect_ended(in_data)
    else:
        LOGGER.error(f"Incorrect status '{in_data.status}'. Should be python boolean.")

@shared_task(name='security.camera_motion_video')
def camera_motion_video(data: dict) -> None:
    in_data = InMotionVideoData(**data)
    camera_video(in_data)

@shared_task()
def discover_alarm(data: dict) -> None:
    in_data = DiscoverAlarmData(**data)
    alarm_discovery.discover_alarm(in_data)

@shared_task(name="alarm.set_alarm_off")
def set_alarm_off(alarm_status_uui):
    AlarmScheduleChangeStatus().turn_off(alarm_status_uui)


@shared_task(name="alarm.set_alarm_on")
def set_alarm_on(alarm_status_uui):
    AlarmScheduleChangeStatus().turn_on(alarm_status_uui)


@shared_task(name="alarm.start_schedule_range")
def start_schedule_range(_schedule_range_uuid):
    alarm_schedule_range.start_schedule_range()


@shared_task(name="alarm.end_schedule_range")
def end_schedule_range(_schedule_range_uuid):
    alarm_schedule_range.end_schedule_range()

@shared_task(name='camera_recording_split_video')
def camera_recording_split_video(event_ref: str) -> None:
    video_manager = alarm_camera_video_manager_factory()
    split = video_manager.split_recording(event_ref)
    if split is True:
        LOGGER.info(f"motion {event_ref} still, schedule next video split.")
        # = 60s
        camera_recording_split_video.apply_async(args=[event_ref], countdown=60)
    else:
        LOGGER.info(f"motion {event_ref} is done, don't split video anymore.")

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
