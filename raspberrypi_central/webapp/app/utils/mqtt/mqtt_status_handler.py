from abc import ABC, abstractmethod
from django.db.models import Model
import alarm.business.alarm as alarm
from mqtt_services.models import MqttServicesConnectionStatusLogs
import mqtt_services.tasks as mqtt_tasks
from utils.mqtt import MQTT, MqttMessage


def split_camera_topic(topic: str):
    """
    Function to extract data from mqtt topic.
    """
    data = topic.split('/')

    try:
        return {
            'type': data[0],
            'service': data[1],
            'device_id': data[2]
        }
    except IndexError as err:
        raise ValueError(f'cannot extract data from {topic}. Should be like `type/service/device_id`.') from err


class OnConnectedHandler(ABC):
    def __init__(self, client: MQTT):
        self._client = client

    def get_client(self):
        return self._client

    @abstractmethod
    def on_connect(self, service_name: str, device_id: str) -> None:
        pass

    @abstractmethod
    def on_disconnect(self, service_name: str, device_id: str) -> None:
        pass


class OnConnectedHandlerLog(OnConnectedHandler):
    """
    Handler that logs events to the database.

    If `status_model` is defined, then it performs a test (for every connect/disconnect call) if the corresponding `running` field
    is set to the received `status` for the given pk device (device retrieve thanks to the `device_id`).
    If not, it creates a task which will handle this failure.
    Thanks to this, the system can monitor if a mqtt connection is "right": connected or disconnected when it should be,
    relying on the database to know the source of truth.
    For example, in the database the alarm status is on and the system receives a mqtt message that indicates a disconnect
    from the alarm.
    """
    def __init__(self, client: MQTT, status_model: Model = None):
        self.status_model = status_model
        super().__init__(client)

    def _is_status_exist(self, service_name: str, device_id: str, status: bool):
        if self.status_model:
            if not alarm.is_status_exists(self.status_model, device_id, status):
                kwargs = {
                    'device_id': device_id,
                    'received_status': status,
                    'service_name': service_name,
                }

                mqtt_tasks.mqtt_status_does_not_match_database.apply_async(kwargs=kwargs)

    def on_connect(self, service_name: str, device_id: str) -> None:
        self._is_status_exist(service_name, device_id, True)
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=True, service_name=service_name)

    def on_disconnect(self, service_name: str, device_id: str) -> None:
        self._is_status_exist(service_name, device_id, False)
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=False, service_name=service_name)


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
        service_name = topic['service']

        if message.payload is True:
            self._handler.on_connect(service_name, device_id)
        else:
            self._handler.on_disconnect(service_name, device_id)
