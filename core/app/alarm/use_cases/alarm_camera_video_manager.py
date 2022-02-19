import logging
from datetime import timedelta
from django.utils import timezone
from typing import Sequence

from utils import mqtt
from camera.models import CameraMotionVideo
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

def _split_messages() -> Sequence[mqtt.MQTTMessage]:
    """
    Loop through opened motions and check if it needs to split video for it.
    """
    motions = current_motions()
    event_refs = [motion.event_ref for motion in motions]

    time_threshold = timezone.now() - timedelta(minutes=1)
    videos = CameraMotionVideo.objects.filter(event_ref__in=event_refs, last_record__lt=time_threshold, is_merged=False)

    messages = []
    for video in videos:
        LOGGER.info(f'video last record: {video.last_record}')
        device_id = video.device.device_id
        record_video_number = video.number_records+1
        video_ref = f'{video.event_ref}-{record_video_number}'

        payload = mqtt.MQTTMessage(
            topic=f"camera/recording/{device_id}/split/{video_ref}"
        )
        messages.append(payload)

    return messages


class AlarmCameraVideoManager:
    def __init__(self, mqtt_client: mqtt.MQTTOneShoot) -> None:
        self._mqtt_client = mqtt_client

    def split_recordings(self, event_ref: str) -> None:
        LOGGER.info('split_recordings event_ref={event_ref}')
        messages = _split_messages()
        self._mqtt_client.multiple(messages, f'split_recordings-{event_ref}')

    def start_recording(self, device_id: str, event_ref: str) -> None:
        video_ref = f'{event_ref}-0'
        payload = mqtt.MQTTMessage(topic=f"camera/recording/{device_id}/start/{video_ref}")
        LOGGER.info(f'start_recording topic={payload.topic} device_id={device_id} video_ref={video_ref}')
        self._mqtt_client.single(payload, f'start_recording-{event_ref}')

    def stop_recording(self, device_id: str, event_ref: str) -> None:
        try:
            last_video = CameraMotionVideo.objects.filter(event_ref=event_ref).order_by('-number_records')[0:1].get()
        except CameraMotionVideo.DoesNotExist:
            LOGGER.error(f'stop_recording impossible: camera motion video not found for event_ref={event_ref}')
            return None

        video_ref = f'{event_ref}-{last_video.number_records}'
        payload = mqtt.MQTTMessage(topic=f"camera/recording/{device_id}/stop/{video_ref}")
        LOGGER.info(f'stop_recording topic={payload.topic} device_id={device_id} video_ref={video_ref}')
        self._mqtt_client.single(payload, f'stop_recording-{event_ref}')

def alarm_camera_video_manager_factory() -> AlarmCameraVideoManager:
    m = mqtt.mqtt_one_shoot_factory()
    return AlarmCameraVideoManager(m)
