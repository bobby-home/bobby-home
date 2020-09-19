import uuid
import logging
from utils.mqtt.mqtt_data import MqttTopicSubscriptionBoolean, MqttTopicFilterSubscription, MqttTopicSubscription, MqttMessage
from utils.mqtt import MQTT
from alarm.tasks import camera_motion_picture, camera_motion_detected
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from functools import partial
from alarm.models import AlarmStatus
from .messaging import alarm_messaging_factory, speaker_messaging_factory


_LOGGER = logging.getLogger(__name__)


def split_camera_topic(topic: str):
    data = topic.split('/')

    return {
        'type': data[0],
        'service': data[1],
        'device_id': data[2]
    }


def on_motion_camera(client: MQTT, message: MqttMessage):
    topic = split_camera_topic(message.topic)

    if message.payload is True:
        print('on motion camera true!')
        data = {
            'device_id': topic['device_id']
        }
        camera_motion_detected.apply_async(kwargs=data)
    else:
        print('on motion camera false!')
        speaker = speaker_messaging_factory(client)
        speaker.publish_speaker_status(topic['device_id'], False)


def on_motion_picture(message: MqttMessage):
    topic = split_camera_topic(message.topic)

    random = uuid.uuid4()
    file_name = f'{random}.jpg'

    # Remember: image is bytearray
    image = message.payload

    filename = default_storage.save(file_name, ContentFile(image))
    picture_path = default_storage.path(filename)

    data = {
        'device_id': topic['device_id'],
        'picture_path': picture_path
    }

    camera_motion_picture.apply_async(kwargs=data)


def on_connected_speaker(client: MQTT, message: MqttMessage):
    topic = split_camera_topic(message.topic)
    speaker_messaging_factory(client).publish_speaker_status(topic['device_id'], False)


def on_connected_camera(client: MQTT, message: MqttMessage):
    topic = split_camera_topic(message.topic)

    device_id = topic['device_id']

    device_status = AlarmStatus.objects.get(device__device_id=device_id)
    alarm_messaging_factory(client).publish_alarm_status(device_status.device.device_id, device_status.running)


def register(mqtt: MQTT):
    mqtt.add_subscribe([
        MqttTopicFilterSubscription(
            topic='motion/#',
            qos=1,
            topics=[
                MqttTopicSubscriptionBoolean('motion/camera/+', partial(on_motion_camera, mqtt)),
                # encoding is set to None because this topic receives a picture as bytes -> decode utf-8 on it will raise an Exception.
                MqttTopicSubscription('motion/picture/+', on_motion_picture),
            ],
        ),
        MqttTopicFilterSubscription(
            topic='connected/camera/+',
            qos=1,
            topics=[
                MqttTopicSubscription('connected/camera/+', partial(on_connected_camera, mqtt)),
                MqttTopicSubscription('connected/speaker/+', partial(on_connected_speaker, mqtt)),
            ]
        )
    ])
