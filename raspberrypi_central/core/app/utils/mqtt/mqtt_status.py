import struct
import json

from utils.json.encoders import DecimalEncoder, EnhancedJSONEncoder
from utils.mqtt import MQTT


class MqttBooleanStatus:
    def __init__(self, mqtt_client: MQTT):
        self._mqtt_client = mqtt_client

    def publish(self, topic: str, message: bool) -> None:
        status_bytes = struct.pack('?', message)
        self._mqtt_client.publish(topic, status_bytes, qos=1, retain=True)


class MqttJsonStatus:
    def __init__(self, mqtt_client: MQTT):
        self._mqtt_client = mqtt_client

    def publish(self, topic: str, status: bool, data=None) -> None:
        payload = {
            'status': status,
            'data': data
        }

        encoded_data = json.dumps(payload, cls=EnhancedJSONEncoder)

        self._mqtt_client.publish(topic, encoded_data, qos=1, retain=True)
