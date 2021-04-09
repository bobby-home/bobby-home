from dataclasses import dataclass
from typing import Optional

from utils.mqtt.mqtt_status import MqttJsonStatus


@dataclass
class CameraData:
    to_analyze: Optional[bool] = None
    stream: Optional[bool] = None


class CameraMessaging:
    """Class to communicate with mqtt cameras.
    """
    def __init__(self, mqtt_status: MqttJsonStatus):
        self._mqtt_status = mqtt_status

    def publish_status(self, device_id: str, status: bool, data: Optional[CameraData] = None) -> None:
        self._mqtt_status.publish(f'status/camera/{device_id}', status, data)


def camera_messaging_factory(mqtt_client):
    mqtt_status = MqttJsonStatus(mqtt_client)

    return CameraMessaging(mqtt_status)
