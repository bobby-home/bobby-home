from camera.detect_motion import DetectMotion
from pathlib import Path 
import paho.mqtt.client as mqtt
import json


class Camera():

    def __init__(self, get_mqtt_client, device_id):
        self._device_id = device_id
        self.get_mqtt_client = get_mqtt_client

    def start(self):
        self.mqtt_client = self.get_mqtt_client(client_name=f'{self._device_id}-rpi4-alarm-motion-DETECT')
        self.mqtt_client.loop_start()
        DetectMotion(self._presenceCallback, self._noMorePresenceCallBack)

    def _presenceCallback(self, byteArr):
        payload = {
            'device_id': self._device_id,
        }

        self.mqtt_client.publish('motion/camera', payload=json.dumps(payload), qos=1)

        self.mqtt_client.publish('motion/picture', payload=byteArr, qos=1)

    def _noMorePresenceCallBack(self):
        payload = {
            'device_id': self._device_id,
        }

        self.mqtt_client.publish('motion/camera/no_more', payload=json.dumps(payload), qos=1)
