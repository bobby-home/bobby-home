from camera.motion import DetectMotion
from pathlib import Path 
from sound.sound import Sound
import paho.mqtt.client as mqtt
import json


class Camera():

    def __init__(self, mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
        self.mqtt_user = mqtt_user
        self.mqtt_pswd = mqtt_pswd
        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port

        self.mqtt_client = self._mqtt_connect()

    def _mqtt_connect(self):
        client = mqtt.Client()
        client.username_pw_set(self.mqtt_user, self.mqtt_pswd)

        client.connect(self.mqtt_hostname, int(self.mqtt_port), keepalive=120)

        return client

    def start(self):
        DetectMotion(self._presenceCallback)

    def _presenceCallback(self, presence: bool, picture_path: str):
        print(f'presence: {presence}')

        payload = {
            # @TODO
            device_id: 'some device id',
        }

        self.mqtt_client.publish('motion/camera', payload=json.dumps(payload))
        # s = Sound()
        # s.alarm()
