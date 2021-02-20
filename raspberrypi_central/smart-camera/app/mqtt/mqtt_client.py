import os
import struct
import logging
from collections import Callable
from typing import List

import paho.mqtt.client as mqtt
from paho.mqtt.reasoncodes import ReasonCodes

_LOGGER = logging.getLogger(__name__)


class MqttClient:
    """Little wrapper around paho mqtt mqtt.

    Centralize the initialization of a new paho mqtt client and add some common methods.
    Keep it little as possible.
    """
    def __init__(self, client_name: str, mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
        client = mqtt.Client(client_id=client_name, protocol=mqtt.MQTTv5)
        client.username_pw_set(mqtt_user, mqtt_pswd)

        client.on_connect = self._mqtt_on_connect
        client.on_disconnect = self._mqtt_on_disconnect

        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port

        self.client = client
        self.on_connected_callbacks: List[Callable[[mqtt.Client], None]] = []

    def connect_keep_status(self, service_name: str, device_id: str):
        """
        Connect to the mqtt broker with information needed to keep track of the service/device_id status (on/off).
        """
        # Will message has to be set before we connect.
        self.client.will_set(f'connected/{service_name}/{device_id}', payload=struct.pack('?', False), qos=1, retain=True)
        self.connect()
        self.client.publish(f'connected/{service_name}/{device_id}', payload=struct.pack('?', True), qos=1, retain=True)

    def connect(self):
        self.client.connect(self.mqtt_hostname, int(self.mqtt_port), keepalive=120)

    @staticmethod
    def _mqtt_on_disconnect(_client, _userdata, rc):
        print(f'_mqtt_on_disconnect reason code: {mqtt.connack_string(rc)}')

    def _mqtt_on_connect(self, _client, _userdata, _flags, rc: ReasonCodes, _properties):
        print(f'_mqtt_on_connect rc: {rc}')

        if rc != mqtt.CONNACK_ACCEPTED:
            _LOGGER.error(
                "Unable to connect to the MQTT broker: %s",
                mqtt.connack_string(rc),
            )
            return

        for callback in self.on_connected_callbacks:
            callback(_client)

def get_mqtt(client_name: str) -> MqttClient:
    return MqttClient(
        client_name,
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT']
    )
