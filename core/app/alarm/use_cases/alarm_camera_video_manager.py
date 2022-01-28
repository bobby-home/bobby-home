from datetime import timedelta
from django.utils import timezone
from typing import Dict, Sequence
import paho.mqtt.publish as publish

from utils import mqtt
from camera.models import CameraMotionVideo
from alarm.business.alarm_motions import current_motions

"""
Alarm camera video manager: manages when to start/end/split videos.
Use cases:
- When a motion is detected -> calls the camera service to start recording.
- When a motion is being -> calls the camera service to split videos.
  This feature allows us to retrieve videos from possible remote devices to send them to the resident (keep them in touch),
  and it also benefits the security. If people break the camera, we still get some parts of the video.
- When a motion stop -> calls the camera service to stop recoding.
"""

def _split_messages() -> Sequence[Dict]:
    """
    Loop through opened motions and check if it needs to split video for it.
    """
    motions = current_motions()
    event_refs = [motion.event_ref for motion in motions]

    time_threshold = timezone.now() - timedelta(minutes=1)
    print(f'time threshold={time_threshold}')

    videos = CameraMotionVideo.objects.filter(event_ref__in=event_refs, last_record__lt=time_threshold, is_merged=False)

    messages = []

    for video in videos:
        print(f'video last record: {video.last_record}')
        device_id = video.device.device_id
        record_video_number = video.number_records+1
        video_ref = f'{video.event_ref}-{record_video_number}'

        payload = {'topic':f"camera/recording/{device_id}/split/{video_ref}", 'payload':"", 'qos': 1, 'retain': False}
        messages.append(payload)

    return messages

def split_manager() -> None:
    messages = _split_messages()
    conf = mqtt.mqtt_config_dict(client_id="alarm_camera_video_manager")
    publish.multiple(messages, **conf)

def start_recording() -> None:
    pass

def stop_recording() -> None:
    pass
