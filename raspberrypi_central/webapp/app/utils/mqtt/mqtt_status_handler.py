from abc import ABC, abstractmethod

from alarm.business.alarm import is_status_exists
from alarm.models import AlarmStatus
from mqtt_services.models import MqttServicesConnectionStatusLogs
from mqtt_services.tasks import mqtt_status_does_not_match_database
from utils.mqtt import MQTT, MqttMessage


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


checkers = {
    'object_detection': {
        'model': AlarmStatus
    }
}


class OnConnectedHandlerLog(OnConnectedHandler):

    def __init__(self, service_name: str, client: MQTT):
        super().__init__(service_name, client)

    def _is_status_exist(self, device_id: str, status: bool):
        if self._service_name in checkers:
            checker = checkers[self._service_name]
            model_ref = checker['model']

            if not is_status_exists(model_ref=model_ref, device_id=device_id, running=False):
                kwargs = {
                    'device_id': device_id,
                    'received_status': status,
                    'service_name': self._service_name,
                }

                mqtt_status_does_not_match_database.apply_async(kwargs=kwargs)

    def on_connect(self, device_id: str) -> None:
        self._is_status_exist(device_id, True)
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=True, service_name=self._service_name)

    def on_disconnect(self, device_id: str) -> None:
        self._is_status_exist(device_id, False)
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=False, service_name=self._service_name)


class OnStatus:
    """
    Class to call the appropriate method on the handler
    depending on the mqtt payload with the extracted device_id from the mqtt topic.
    This helps to keep all mqtt services implementation the same.
    """

    def __init__(self, handler: OnConnectedHandler):
        self._handler = handler

    def on_connected(self, message: MqttMessage) -> None:
        topic = split_camera_topic(message.topic)
        device_id = topic['device_id']

        if message.payload is True:
            self._handler.on_connect(device_id)
        else:
            self._handler.on_disconnect(device_id)
