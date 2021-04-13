from dataclasses import dataclass

from hello_django.loggers import LOGGER
from utils.mqtt.mqtt_data import MqttTopicFilterSubscription, MqttTopicSubscription, \
    MqttMessage, MqttTopicSubscriptionJson
from utils.mqtt import MQTT
import alarm.tasks as tasks
from alarm.tasks import camera_motion_detected

from utils.mqtt.mqtt_status_handler import bind_on_connected
from alarm.business.alarm import register_ping
from alarm.communication.on_connected_services import OnConnectedObjectDetectionHandler, OnConnectedSpeakerHandler, \
    OnConnectedCamera
import os
import hello_django.settings as settings


DEVICE_ID = os.environ['DEVICE_ID']

def split_camera_topic(topic: str, is_event_ref = False):
    data = topic.split('/')

    r_data = {
        'type': data[0],
        'service': data[1],
        'device_id': data[2]
    }

    if is_event_ref:
        r_data['event_ref'] = data[3]

        if len(data) == 5:
            r_data['status'] = data[4]

    return r_data


def on_motion_camera(message: MqttMessage):
    topic = split_camera_topic(message.topic)
    payload = message.payload

    LOGGER.info(f'on_motion_camera payload={payload}')

    data = {
        'device_id': topic['device_id'],
        'event_ref': payload['event_ref'],
        'status': payload['status'],
        'seen_in': {},
    }

    if data['status'] is True:
        data['seen_in'] = payload['seen_in']

    if data['event_ref'] != '0':
        # 0 = initialization
        camera_motion_detected.apply_async(kwargs=data)


def on_motion_video(message: MqttMessage) -> None:
    topic = split_camera_topic(message.topic, True)
    LOGGER.info(f'on_motion_video: topic={topic} {message.topic}')

    data = {
        'device_id': topic['device_id'],
        'video_ref': topic['event_ref'],
    }

    # The system has some latency to save the video,
    # so we add a little countdown so the video will more likely be available after x seconds.
    tasks.camera_motion_video.apply_async(kwargs=data, countdown=3)

def on_motion_picture(message: MqttMessage):
    topic = split_camera_topic(message.topic, True)

    event_ref = topic['event_ref']
    status = topic['status']

    bool_status = None
    if status == '0':
        bool_status = False
    elif status == '1':
        bool_status = True
    else:
        raise ValueError(f'Status {status} should be "0" or "1".')

    LOGGER.info(f'on_motion_picture even_ref={event_ref}')

    if event_ref == "0":
        # Initialization: no motion
        return

    file_name = f'{event_ref}.jpg'

    # Remember: image is bytearray
    image = message.payload

    """
    Warning: hacky thing.
    - We need to save the file here because we cannot send it to a Task (memory consumption!).
    - So we save manually the file to the disk at the right place for Django.
    - But we can't use model.file.save('name.jpg', content, True) because we do not have the model instance here this is the task job.
    - So we go with low-level API.
    - at the end, picture_path is an absolute path e.g: "/usr/src/app/media/1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg"
    """

    picture_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(picture_path, 'wb') as f:
        f.write(image)

    data = {
        'device_id': topic['device_id'],
        'picture_path': picture_path,
        'event_ref': event_ref,
        'status': bool_status,
    }

    tasks.camera_motion_picture.apply_async(kwargs=data)

@dataclass
class PingData:
    device_id: str
    service_name: str

def on_ping_data_from_topic(topic: str) -> PingData:
    data = topic.split('/')
    return PingData(data[2], data[1])


def on_ping(message: MqttMessage) -> None:
    data = on_ping_data_from_topic(message.topic)
    register_ping(data.device_id, data.service_name)


def register(mqtt: MQTT):
    def inner(mqtt: MQTT):
        mqtt.add_subscribe([
            MqttTopicFilterSubscription(
                topic='motion/#',
                qos=1,
                topics=[
                    MqttTopicSubscriptionJson('motion/camera/+', on_motion_camera),
                    MqttTopicSubscription('motion/picture/+/+/+', on_motion_picture),
                    MqttTopicSubscription('motion/video/+/+', on_motion_video),
                ],
            ),
            MqttTopicFilterSubscription(
                # ping/{service_name}/{device_id}
                topic='ping/+/+',
                qos=1,
                topics=[
                    MqttTopicSubscription('ping/+/+', on_ping)
                ]
            ),
        ])

    mqtt.on_connected_callbacks.append(inner)
