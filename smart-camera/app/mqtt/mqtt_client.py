import os
import struct
import logging
from typing import Callable
from typing import Any, List

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

        self._client = client
        self._on_connected_callbacks: List[Callable[[mqtt.Client], None]] = []

        self._service_name = None
        self._device_id = None

    @property
    def client(self) -> mqtt.Client:
        return self._client

    def add_on_connected_callbacks(self, cb: Callable) -> None:
        self._on_connected_callbacks.append(cb)

    def connect_keep_status(self, service_name: str, device_id: str):
        """
        Connect to the mqtt broker with information needed to keep track of the service/device_id status (on/off).
        """
        self._service_name = service_name
        self._device_id = device_id

        # Will message has to be set before we connect.
        self._client.will_set(f'connected/{service_name}/{device_id}', payload=struct.pack('?', False), qos=1, retain=True)
        self.connect()
        self._client.publish(f'connected/{service_name}/{device_id}', payload=struct.pack('?', True), qos=1, retain=True)

    def connect(self):
        self._client.connect(self.mqtt_hostname, int(self.mqtt_port), keepalive=120)

    def disconnect(self):
        if self._service_name and self._device_id:
            self._client.publish(f'connected/{self._service_name}/{self._device_id}', payload=struct.pack('?', False), qos=1, retain=True)
        self._client.disconnect()

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

        for callback in self._on_connected_callbacks:
            callback(_client)

def get_mqtt(client_name: str) -> MqttClient:
    return MqttClient(
        client_name,
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT']
    )
