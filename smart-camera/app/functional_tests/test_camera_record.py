import os
import logging
import time
from unittest import TestCase
from uuid import uuid4

LOGGER = logging.getLogger(__name__)

import paho.mqtt.client as mqtt
import pathlib
"""
- Run the whole application before running this test.
But I don't need any code from it, tests should be independent.

- Create MQTT client to tests.
- start_record
    -> test -before file has been created.
- split_record
    -> file has been created
    -> + mqtt ack publish
- stop_record
    -> file has been created
    -> + mqtt ack publish

"""

class TestCaseBase(TestCase):
    def assertIsFile(self, path):
        ppath = pathlib.Path(path)
        if not ppath.resolve().is_file():
            parent = ppath.parent
            files = [p for p in parent.iterdir() if p.is_file()]
            raise AssertionError(f"File does not exist: {str(path)} files are: {files}")

class IntegrationCameraRecordTestCase(TestCaseBase):
    def setUp(self) -> None:
        self.base_video_path = os.environ['MEDIA_FOLDER']
        self.device_id = os.environ['DEVICE_ID']
        user = os.environ['MQTT_USER']
        password = os.environ['MQTT_PASSWORD']
        self.hostname = os.environ['MQTT_HOSTNAME']
        self.port = int(os.environ['MQTT_PORT'])

        self.client = mqtt.Client(client_id="test_camera_record")
        self.client.username_pw_set(user, password)

        self.video_ref = str(uuid4())
        return super().setUp()

    def _get_start_ack_topic(self, video_ref: str):
        return f'ack/video/started/#'

    def _get_start_topic(self, video_ref: str):
        return f'camera/recording/{self.device_id}/start/{video_ref}'

    def _get_camera_connected_topic(self):
        return f'connected/camera/{self.device_id}'

    def _start_camera(self) -> None:
        self.client.publish(f'status/camera_manager/{self.device_id}', payload='{"status": "true", "data": {}}', qos=2)

    def on_connected_camera(self, _client, _userdata, msg):
        start_topic = self._get_start_topic(self.video_ref)
        self.client.publish(start_topic, qos=2)
        # wait for the recorder to be up
        # as of today I don't have a feedback when it comes to life.
        time.sleep(3)

    def on_ack_start(self,  _client, _userdata, msg):
        expected_video_path = os.path.join(self.base_video_path, f'{self.video_ref}-before.h264')
        self.assertIsFile(expected_video_path)
        self.client.disconnect()

    def test_start_record(self):
        ack_topic = self._get_start_ack_topic(self.video_ref)
        camera_connected_topic = self._get_camera_connected_topic()

        self.client.connect(self.hostname, self.port)

        self.client.subscribe(ack_topic)
        self.client.subscribe(camera_connected_topic)

        self.client.message_callback_add(ack_topic, self.on_ack_start)
        self.client.message_callback_add(camera_connected_topic, self.on_connected_camera)

        self._start_camera()
        self.client.loop_forever()

