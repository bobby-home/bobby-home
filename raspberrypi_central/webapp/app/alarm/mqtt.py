import uuid
from standalone.mqtt import MqttTopicFilterSubscription, MqttTopicSubscription, MqttMessage, MqttTopicSubscriptionJson, MQTT
from alarm.tasks import camera_motion_picture, camera_motion_detected
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from functools import partial
from alarm.models import AlarmStatus


def on_motion_camera(message: MqttMessage):
    payload = message.payload

    data = {
        'device_id': payload['device_id']
    }

    camera_motion_detected.apply_async(kwargs=data)


def on_motion_picture(message: MqttMessage):
    random = uuid.uuid4()
    file_name = f'{random}.jpg'

    # Remember: image is bytearray
    image = message.payload

    filename = default_storage.save(file_name, ContentFile(image))
    picture_path = default_storage.path(filename)

    data = {
        'picture_path': picture_path
    }

    camera_motion_picture.apply_async(kwargs=data)


def on_motion_camera_no_more(client: MQTT, message: MqttMessage):
    client.publish('status/sound', str(False), qos=1)


def on_status_alarm(client: MQTT, message: MqttMessage):
    status = AlarmStatus.objects.get_status()

    client.publish('status/alarm', message=str(status), qos=1)


def on_status_sound(client: MQTT, message: MqttMessage):
    client.publish('status/sound', message=str(False), qos=1)


def register(mqtt: MQTT):
    mqtt.add_subscribe([
        MqttTopicFilterSubscription(
            topic='motion/#',
            qos=1,
            topics=[
                MqttTopicSubscriptionJson('motion/camera', on_motion_camera),
                MqttTopicSubscription('motion/picture', on_motion_picture, encoding=None),
                MqttTopicSubscription('motion/camera/no_more', partial(on_motion_camera_no_more, mqtt)),
            ],
        ),
        MqttTopicFilterSubscription(
            topic='ask/#',
            qos=1,
            topics=[
                MqttTopicSubscription('ask/status/alarm', partial(on_status_alarm, mqtt)),
                MqttTopicSubscription('ask/status/sound', partial(on_status_sound, mqtt)),
            ]
        )
    ])
