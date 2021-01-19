import os
import paho.mqtt.client as mqtt


class MqttClient:
    """Little wrapper around paho mqtt mqtt.

    Centralize the initialization of a new paho mqtt client.
    It does not connect directly to allow to set a will_message for example.
    """
    def __init__(self, client_name: str, mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
        client = mqtt.Client(client_id=client_name, clean_session=False)
        client.username_pw_set(mqtt_user, mqtt_pswd)

        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port

        self.client = client

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
