import os
import paho.mqtt.client as mqtt


def create_mqtt_client(client_name: str, mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
    client = mqtt.Client(client_id=client_name, clean_session=False)
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    # mqtt.Client
    return client


def get_mqtt_client(client_name: str):
    return create_mqtt_client(
        client_name,
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT']
    )
