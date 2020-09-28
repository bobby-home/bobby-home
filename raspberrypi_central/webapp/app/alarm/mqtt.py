import uuid
import logging

from utils.mqtt.mqtt_data import MqttTopicSubscriptionBoolean, MqttTopicFilterSubscription, MqttTopicSubscription, \
    MqttMessage
from utils.mqtt import MQTT
from alarm.tasks import camera_motion_picture, camera_motion_detected
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from functools import partial
from alarm.models import AlarmStatus, CameraRectangleROI

from utils.mqtt.mqtt_status_handler import OnConnectedHandler, OnStatus
from .messaging import alarm_messaging_factory, speaker_messaging_factory
from django.forms.models import model_to_dict


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
        data = {
            'device_id': topic['device_id']
        }
        camera_motion_detected.apply_async(kwargs=data)
    else:
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


class OnConnectedCameraHandler(OnConnectedHandler):

    def on_connected(self, device_id: str) -> None:
        device_status = AlarmStatus.objects.get(device__device_id=device_id)
        device_roi = CameraRectangleROI.objects.all().first()
        # TODO: get ROI from database linked to this device_id
        # roi = {'x': 128, 'y': 185, 'w': 81, 'h': 76, 'definition_width': 300, 'definition_height': 300}

        # Otherwise you'll get error: "Object of type <ModelClass> is not JSON serializable"
        device_roi_obj = model_to_dict(device_roi)

        alarm_messaging_factory(self._client) \
            .publish_alarm_status(device_status.device.device_id, device_status.running, device_roi_obj)


class OnConnectedSpeakerHandler(OnConnectedHandler):

    def on_connected(self, device_id: str) -> None:
        speaker_messaging_factory(self._client).publish_speaker_status(device_id, False)


def bind_on_connected(mqtt: MQTT, service_name: str, handler) -> MqttTopicSubscriptionBoolean:
    handler_instance: OnConnectedHandler = handler(mqtt)
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
                MqttTopicSubscriptionBoolean('motion/camera/+', partial(on_motion_camera, mqtt)),
                MqttTopicSubscription('motion/picture/+', on_motion_picture),
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
