import logging
from typing import Callable

from hello_django.loggers import LOGGER
from utils.mqtt.mqtt_data import MqttTopicSubscriptionBoolean, MqttTopicFilterSubscription, MqttTopicSubscription, \
    MqttMessage, MqttTopicSubscriptionJson
from utils.mqtt import MQTT
from alarm.tasks import camera_motion_picture, camera_motion_detected
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from utils.mqtt.mqtt_status_handler import OnConnectedHandler, OnStatus, OnConnectedHandlerLog
from .communication.out_alarm import notify_alarm_status_factory
from .messaging import speaker_messaging_factory


def split_camera_topic(topic: str, is_event_ref = False):
    data = topic.split('/')

    r_data = {
        'type': data[0],
        'service': data[1],
        'device_id': data[2]
    }

    if is_event_ref:
        r_data['event_ref'] = data[3]
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


def on_motion_picture(message: MqttMessage):
    topic = split_camera_topic(message.topic, True)

    event_ref = topic['event_ref']
    status = topic['status']

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
    filename = default_storage.save(file_name, ContentFile(image))
    picture_path = default_storage.path(filename)

    data = {
        'device_id': topic['device_id'],
        'picture_path': picture_path,
        'event_ref': event_ref,
        'status': status,
    }

    camera_motion_picture.apply_async(kwargs=data)


class OnConnectedCameraHandler(OnConnectedHandlerLog):

    def on_connect(self, device_id: str) -> None:
        mx = notify_alarm_status_factory(self.get_client)
        mx.publish_device_connected(device_id)

        return super().on_connect(device_id)


class OnConnectedSpeakerHandler(OnConnectedHandlerLog):
    pass


def bind_on_connected(mqtt, service_name: str, handler_constructor: Callable[[str, MQTT], OnConnectedHandler]) -> MqttTopicSubscriptionBoolean:
    handler_instance = handler_constructor(service_name, mqtt)
    on_status = OnStatus(handler_instance)

    return MqttTopicSubscriptionBoolean(f'connected/{service_name}/+', on_status.on_connected)


def register(mqtt: MQTT):
    speaker = bind_on_connected(mqtt, 'speaker', OnConnectedSpeakerHandler)
    camera = bind_on_connected(mqtt, 'camera', OnConnectedCameraHandler)

    mqtt.add_subscribe([
        MqttTopicFilterSubscription(
            topic='motion/#',
            qos=1,
            topics=[
                MqttTopicSubscriptionJson('motion/camera/+', on_motion_camera),
                MqttTopicSubscription('motion/picture/+/+/+', on_motion_picture),
            ],
        ),
        camera,
        speaker
    ])
