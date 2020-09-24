import struct
from abc import ABCMeta, abstractmethod
import json
from utils.mqtt import MQTT


class MqttBooleanStatus:
    def __init__(self, mqtt_client: MQTT):
        self._mqtt_client = mqtt_client

    def publish(self, topic, message: bool):
        status_bytes = struct.pack('?', message)
        self._mqtt_client.publish(topic, status_bytes, )


class MqttJsonStatus:
    def __init__(self, mqtt_client: MQTT):
        self._mqtt_client = mqtt_client

    def publish(self, topic, msg: bool, data):
        # @TODO: merge with data passed by param, but how do we do this? :)
        data = json.dumps(msg)

        self._mqtt_client.publish(topic, data)
