import uuid
from standalone.mqtt import MqttTopicFilterSubscription, MqttTopicSubscription, MqttMessage, MQTT
from alarm.tasks import camera_motion_picture, camera_motion_detected
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from functools import partial
from alarm.models import AlarmStatus
from .messaging import alarm_messaging_factory, SpeakerMessaging


def split_camera_topic(topic: str):
    data = topic.split('/')

    return {
        'type': data[0],
        'service': data[1],
        'device_id': data[2]
    }


def on_motion_camera(message: MqttMessage):
    topic = split_camera_topic(message.topic)

    data = {
        'device_id': topic['device_id']
    }

    camera_motion_detected.apply_async(kwargs=data)


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


def on_motion_camera_no_more(client: MQTT, message: MqttMessage):
    topic = split_camera_topic(message.topic)

    speaker = SpeakerMessaging(client)
    speaker.publish_speaker_status(topic['device_id'], False)


def on_connected_speaker(client: MQTT, message: MqttMessage):
    topic = split_camera_topic(message.topic)
    SpeakerMessaging(client).publish_speaker_status(topic['device_id'], False)


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
                MqttTopicSubscription('motion/camera/+', on_motion_camera),
                # encoding is set to None because this topic receives a picture as bytes -> decode utf-8 on it will raise an Exception.
                MqttTopicSubscription('motion/picture/+', on_motion_picture, encoding=None),
                MqttTopicSubscription('motion/no_more/+', partial(on_motion_camera_no_more, mqtt)),
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
