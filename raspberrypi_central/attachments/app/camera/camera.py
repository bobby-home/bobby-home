from camera.detect_motion import DetectMotion
from pathlib import Path 
from sound.sound import Sound
import paho.mqtt.client as mqtt
import json


class Camera():

    def __init__(self, get_mqtt_client, device_id):
        self._device_id = device_id
        self.mqtt_client = get_mqtt_client(client_name=f'{device_id}-rpi4-alarm-motion-DETECT')

    def start(self):
        DetectMotion(self._presenceCallback)

    def _presenceCallback(self, presence: bool, byteArr):
        payload = {
            'device_id': self._device_id,
        }

        self.mqtt_client.publish('motion/camera', payload=json.dumps(payload), qos=1)

        self.mqtt_client.publish('motion/picture', payload=byteArr, qos=1)
        # s = Sound()
        # s.alarm()
