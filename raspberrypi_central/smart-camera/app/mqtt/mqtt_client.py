import os
import struct

import paho.mqtt.client as mqtt


class MqttClient:
    """Little wrapper around paho mqtt mqtt.

    Centralize the initialization of a new paho mqtt client and add some common methods.
    Keep it little as possible.
    """
    def __init__(self, client_name: str, mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
        # todo: migrate to mqtt v5 -> protocol=mqtt.MQTTv5
        client = mqtt.Client(client_id=client_name)
        client.username_pw_set(mqtt_user, mqtt_pswd)

        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port

        self.client = client

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


def get_mqtt(client_name: str) -> MqttClient:
    return MqttClient(
        client_name,
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT']
    )
