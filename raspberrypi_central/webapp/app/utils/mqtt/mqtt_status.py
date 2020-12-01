import struct
import json
from decimal import Decimal

from utils.json.decimal_encoder import DecimalEncoder
from utils.mqtt import MQTT


class MqttBooleanStatus:
    def __init__(self, mqtt_client: MQTT):
        self._mqtt_client = mqtt_client

    def publish(self, topic, message: bool) -> None:
        status_bytes = struct.pack('?', message)
        self._mqtt_client.publish(topic, status_bytes, qos=1, retain=True)


class MqttJsonStatus:
    def __init__(self, mqtt_client: MQTT):
        self._mqtt_client = mqtt_client

    def publish(self, topic, msg: bool, data=None) -> None:
        payload = {
            'status': msg,
            'data': data
        }

        encoded_data = json.dumps(payload, cls=DecimalEncoder)

        print(f'mqtt json status: {payload} {topic}')

        self._mqtt_client.publish(topic, encoded_data, qos=1, retain=True)
