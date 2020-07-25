from mqtt.mqtt_camera import MqttCamera
from camera.camera_manager import CameraManager as CM
from camera.camera_factory import camera_factory
from camera.camera import Camera
import paho.mqtt.client as mqtt
from functools import partial
import os
import json


def create_mqtt_client(mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
    client = mqtt.Client(client_id='rpi4-alarm-motion', clean_session=False)
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    # mqtt.Client
    return client

mqtt_client = create_mqtt_client(
    os.environ['MQTT_USER'],
    os.environ['MQTT_PASSWORD'],
    os.environ['MQTT_HOSTNAME'],
    os.environ['MQTT_PORT']
)

MQTT_ALARM_CAMERA_TOPIC = os.environ['MQTT_ALARM_CAMERA_TOPIC']

camera_factory = partial(camera_factory, mqtt_client)

manager = CM(camera_factory)
mqtt_camera_manager = MqttCamera(mqtt_client, manager, MQTT_ALARM_CAMERA_TOPIC)

mqtt_client.loop_forever()
