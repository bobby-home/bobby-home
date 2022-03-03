import logging
from datetime import timedelta
from django.utils import timezone
from typing import Sequence

from utils import mqtt
from camera.models import CameraMotionDetected, CameraMotionVideo
from alarm.business.alarm_motions import current_motions

LOGGER = logging.getLogger(__name__)

"""
Alarm camera video manager: manages when to start/end/split videos.
Use cases:
- When a motion is detected -> calls the camera service to start recording.
- When a motion is being -> calls the camera service to split videos.
  This feature allows us to retrieve videos from possible remote devices to send them to the resident (keep them in touch),
  and it also benefits the security. If people break the camera, we still get some parts of the video.
- When a motion stop -> calls the camera service to stop recoding.
"""

class AlarmCameraVideoManager:
    def __init__(self, mqtt_client: mqtt.MQTTOneShoot) -> None:
        self._mqtt_client = mqtt_client

    def split_recording(self, event_ref: str) -> bool:
        LOGGER.info(f'split_recording event_ref={event_ref}')

        try:
            camera_motion = CameraMotionDetected.objects.get(
                closed_by_system=False,
                motion_ended_at__isnull=True,
                event_ref=event_ref)

            try:
                video = CameraMotionVideo.objects.get(event_ref=event_ref)
                record_video_number = video.number_records+1
                timediff_seconds = (timezone.now() - video.last_record).total_seconds()
                LOGGER.info(f'last record found was {timediff_seconds} seconds ago.')
            except CameraMotionVideo.DoesNotExist:
                # it's the first split video.
                record_video_number = 1

            device_id = camera_motion.device.device_id
            video_ref = f'{camera_motion.event_ref}-{record_video_number}'


            LOGGER.info(f'split_recording event_ref={event_ref} video_ref={video_ref} device_id={device_id}')
            payload = mqtt.MQTTSendMessage(
                topic=f"camera/recording/{device_id}/split/{video_ref}"
            )
            self._mqtt_client.single(payload, client_id=f'split_recording-{event_ref}')
            return True
        except CameraMotionDetected.DoesNotExist:
            return False

    def start_recording(self, device_id: str, event_ref: str) -> None:
        video_ref = f'{event_ref}-0'
        payload = mqtt.MQTTSendMessage(topic=f"camera/recording/{device_id}/start/{video_ref}")
        LOGGER.info(f'start_recording topic={payload.topic} device_id={device_id} video_ref={video_ref}')
        self._mqtt_client.single(payload, f'start_recording-{event_ref}')

    def stop_recording(self, device_id: str, event_ref: str) -> None:
        try:
            last_video = CameraMotionVideo.objects.filter(event_ref=event_ref).order_by('-number_records')[0:1].get()
        except CameraMotionVideo.DoesNotExist:
            LOGGER.error(f'stop_recording impossible: camera motion video not found for event_ref={event_ref}')
            return None

        video_ref = f'{event_ref}-{last_video.number_records}'
        payload = mqtt.MQTTSendMessage(topic=f"camera/recording/{device_id}/end/{video_ref}")
        LOGGER.info(f'stop_recording topic={payload.topic} device_id={device_id} video_ref={video_ref}')
        self._mqtt_client.single(payload, f'stop_recording-{event_ref}')

def alarm_camera_video_manager_factory() -> AlarmCameraVideoManager:
    m = mqtt.mqtt_one_shoot_factory()
    return AlarmCameraVideoManager(m)
