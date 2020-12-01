from abc import ABC, abstractmethod
import logging

from mqtt_services.models import MqttServicesConnectionStatusLogs
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
    def __init__(self, service_name: str, client: MQTT):
        self._client = client
        self._service_name = service_name


    def get_client(self):
        return self._client

    @abstractmethod
    def on_connect(self, device_id: str) -> None:
        pass

    @abstractmethod
    def on_disconnect(self, device_id: str) -> None:
        pass


class OnConnectedHandlerLog(OnConnectedHandler):
    def on_connect(self, device_id: str) -> None:
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=True, service_name=self._service_name)

    def on_disconnect(self, device_id: str) -> None:
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=False, service_name=self._service_name)


class OnStatus:
    def __init__(self, handler: OnConnectedHandler):
        self._handler = handler

    def on_connected(self, message: MqttMessage) -> None:
        topic = split_camera_topic(message.topic)
        device_id = topic['device_id']

        if message.payload is True:
            self._handler.on_connect(device_id)
        else:
            self._handler.on_disconnect(device_id)
