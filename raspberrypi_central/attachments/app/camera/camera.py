from camera.motion import DetectMotion
from pathlib import Path 
from sound.sound import Sound
import paho.mqtt.client as mqtt
import json
import os


def create_mqtt_client(mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
    client = mqtt.Client(client_id='rpi4-alarm-motion-DETECT', clean_session=False)
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    # mqtt.Client
    return client

class Camera():

    def __init__(self, _):
        mqtt_client = create_mqtt_client(
            os.environ['MQTT_USER'],
            os.environ['MQTT_PASSWORD'],
            os.environ['MQTT_HOSTNAME'],
            os.environ['MQTT_PORT']
        )

        self.mqtt_client = mqtt_client

    def start(self):
        DetectMotion(self._presenceCallback)

    def _presenceCallback(self, presence: bool, picture_path: str):
        payload = {
            # @TODO
            'device_id': 'some device id',
        }

        self.mqtt_client.publish('motion/camera', payload=json.dumps(payload), qos=1)

        with open(picture_path, 'rb') as image:
            filecontent = image.read()
            byteArr = bytes(filecontent)

        self.mqtt_client.publish('motion/picture', payload=byteArr, qos=1)
        # s = Sound()
        # s.alarm()
