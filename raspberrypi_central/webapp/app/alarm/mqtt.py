import uuid
import logging

from utils.mqtt.mqtt_data import MqttTopicSubscriptionBoolean, MqttTopicFilterSubscription, MqttTopicSubscription, \
    MqttMessage, MqttTopicSubscriptionJson
from utils.mqtt import MQTT
from alarm.tasks import camera_motion_picture, camera_motion_detected
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from functools import partial

from utils.mqtt.mqtt_status_handler import OnConnectedHandler, OnStatus
from .communication.alarm import NotifyAlarmStatus
from .messaging import speaker_messaging_factory
from .models import AlarmStatus

_LOGGER = logging.getLogger(__name__)


def split_camera_topic(topic: str, is_event_ref = False):
    data = topic.split('/')

    data = {
        'type': data[0],
        'service': data[1],
        'device_id': data[2]
    }

    if is_event_ref:
        data['event_ref'] = data[3]

    return data


def on_motion_camera(client: MQTT, message: MqttMessage):
    topic = split_camera_topic(message.topic)
    payload = message.payload

    if payload['status'] is True:
        data = {
            'device_id': topic['device_id'],
            'seen_in': payload['seen_in']
        }
        camera_motion_detected.apply_async(kwargs=data)
    else:
        speaker = speaker_messaging_factory(client)
        speaker.publish_speaker_status(topic['device_id'], False)


def on_motion_picture(message: MqttMessage):
    topic = split_camera_topic(message.topic, True)

    event_ref = topic['event_ref']
    file_name = f'{event_ref}.jpg'

    # Remember: image is bytearray
    image = message.payload

    filename = default_storage.save(file_name, ContentFile(image))
    picture_path = default_storage.path(filename)

    data = {
        'device_id': topic['device_id'],
        'picture_path': picture_path,
        'event_ref': event_ref,
    }

    camera_motion_picture.apply_async(kwargs=data)


class OnConnectedCameraHandler(OnConnectedHandler):

    def on_connected(self, device_id: str) -> None:
        mx = NotifyAlarmStatus(self.get_client)
        mx.publish(device_id)


class OnConnectedSpeakerHandler(OnConnectedHandler):

    def on_connected(self, device_id: str) -> None:
        speaker_messaging_factory(self._client).publish_speaker_status(device_id, False)


def bind_on_connected(service_name: str, handler_instance) -> MqttTopicSubscriptionBoolean:
    on_status = OnStatus(handler_instance)

    return MqttTopicSubscriptionBoolean(f'connected/{service_name}/+', on_status.on_connected)


def register(mqtt: MQTT):
    on_connected_speaker = OnConnectedSpeakerHandler(mqtt)
    on_connected_camera = OnConnectedCameraHandler(mqtt)

    speaker = bind_on_connected('speaker', on_connected_speaker)
    camera = bind_on_connected('camera', on_connected_camera)

    mqtt.add_subscribe([
        MqttTopicFilterSubscription(
            topic='motion/#',
            qos=1,
            topics=[
                MqttTopicSubscriptionJson('motion/camera/+', partial(on_motion_camera, mqtt)),
                MqttTopicSubscription('motion/picture/+/+', on_motion_picture),
            ],
        ),
        MqttTopicFilterSubscription(
            topic='connected/camera/+',
            qos=1,
            topics=[
                speaker, camera
            ]
        )
    ])
