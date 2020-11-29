from abc import ABC, abstractmethod
import logging

from utils.mqtt import MQTT, MqttMessage

_LOGGER = logging.getLogger(__name__)


def split_camera_topic(topic: str):
    data = topic.split('/')

    return {
        'type': data[0],
        'service': data[1],
        'device_id': data[2]
    }


class OnConnectedHandler(ABC):
    def __init__(self, client: MQTT):
        self._client = client

    def get_client(self):
        return self._client

    @abstractmethod
    def on_connected(self, device_id: str) -> None:
        pass


class OnStatus:
    def __init__(self, handler: OnConnectedHandler):
        self._handler = handler

    def on_connected(self, message: MqttMessage) -> None:
        topic = split_camera_topic(message.topic)
        device_id = topic['device_id']

        if message.payload is True:
            self._handler.on_connected(device_id)
        else:
            _LOGGER.error(f'We lost the mqtt connection with {device_id}')
