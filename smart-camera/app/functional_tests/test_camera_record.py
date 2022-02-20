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
        return f'ack/video/started/{self.device_id}/{video_ref}'

    def _get_start_topic(self, video_ref: str):
        return f'camera/recording/{self.device_id}/start/{video_ref}'

    def _start_camera(self) -> None:
        self.client.publish(f'status/camera_manager/{self.device_id}', payload='{"status": "true", "data": {}}', qos=2)

    def on_ack_start(self, **_kwargs):
        expected_video_path = os.path.join(self.base_video_path, f'{self.video_ref}-before.h264')
        self.assertIsFile(expected_video_path)
        self.client.disconnect()

    def test_start_record(self):
        start_topic = self._get_start_topic(self.video_ref)
        ack_topic = self._get_start_ack_topic(self.video_ref)

        time.sleep(2)

        self.client.on_message = self.on_ack_start
        self.client.subscribe(ack_topic)
        self.client.connect(self.hostname, self.port)
        self._start_camera()
        time.sleep(3)
        self.client.publish(start_topic, qos=2)
        LOGGER.error('hello world, please see me')
        self.client.loop_forever()

