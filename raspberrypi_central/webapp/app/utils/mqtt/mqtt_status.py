import struct
import logging


class MqttStatus():
    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    def publish(self, topic, message: bool):
        status_bytes = struct.pack('?', message)
        self._mqtt_client.publish(topic, status_bytes, qos=1, retain=True)
