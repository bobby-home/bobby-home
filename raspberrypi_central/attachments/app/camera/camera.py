from camera.motion import DetectMotion
from pathlib import Path 
from sound.sound import Sound
import paho.mqtt.client as mqtt
import json


class Camera():

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def start(self):
        DetectMotion(self._presenceCallback)

    def _presenceCallback(self, presence: bool, picture_path: str):
        print(f'presence: {presence}')

        payload = {
            # @TODO
            'device_id': 'some device id',
        }

        infot = self.mqtt_client.publish('motion/camera', payload=json.dumps(payload), qos=1)
        # s = Sound()
        # s.alarm()

    def __del__(self):
        print('Del of Camera')
