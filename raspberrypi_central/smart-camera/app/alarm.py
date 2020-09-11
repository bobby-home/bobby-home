from mqtt.mqtt_status_manage_thread import MqttStatusManageThread
from thread.thread_manager import ThreadManager
from camera.camera_factory import camera_factory
from camera.play_sound import PlaySound
from camera.camera import Camera
import paho.mqtt.client as mqtt
from functools import partial
import os
import json
from mqtt.mqtt_client import get_mqtt_client


mqtt_client = get_mqtt_client(f"{os.environ['DEVICE_ID']}-rpi4-alarm-motion")

MQTT_ALARM_CAMERA_TOPIC = 'status/alarm'

camera_factory = partial(camera_factory, get_mqtt_client)

manager = ThreadManager(camera_factory)
MqttStatusManageThread(mqtt_client, manager, MQTT_ALARM_CAMERA_TOPIC)

def play_sound_factory():
    return PlaySound()

sound_manager = ThreadManager(play_sound_factory)
MqttStatusManageThread(mqtt_client, sound_manager, 'status/sound')

mqtt_client.loop_forever()
