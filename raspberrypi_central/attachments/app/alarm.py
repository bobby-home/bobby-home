from mqtt.mqtt_status_camera import MqttStatusCamera
from camera.camera_manager import CameraManager
from camera.camera_factory import camera_factory
from camera.camera import Camera
import paho.mqtt.client as mqtt
from functools import partial
import os
import json
from mqtt.mqtt_client import get_mqtt_client
import os

mqtt_client = get_mqtt_client(f"{os.environ['DEVICE_ID']}-rpi4-alarm-motion")

MQTT_ALARM_CAMERA_TOPIC = os.environ['MQTT_ALARM_CAMERA_TOPIC']

camera_factory = partial(camera_factory, get_mqtt_client)

manager = CameraManager(camera_factory)
mqtt_camera_manager = MqttStatusCamera(mqtt_client, manager, MQTT_ALARM_CAMERA_TOPIC)

mqtt_client.loop_forever()
