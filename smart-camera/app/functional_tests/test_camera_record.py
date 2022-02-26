import os
import logging
import time
from typing import Optional
from unittest import TestCase
from uuid import uuid4
import paho.mqtt.client as mqtt
import pathlib

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

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

        self.split_number = 0
        self.video_ref = str(uuid4())

    def tearDown(self) -> None:
        self._stop_camera_video(self.split_number)
        for file in os.listdir(self.base_video_path):
            path = os.path.join(self.base_video_path, file)

            LOGGER.info(f'tearDown deleting file {file}')
            os.remove(path)

    def _get_camera_connected_topic(self):
        return f'connected/camera/{self.device_id}'

    def _get_start_ack_topic(self, video_ref: str):
        """
        When we start a video, the camera publishes on this topic.
        The last parameter is the video_ref.
        """
        return f'ack/video/started/{self.device_id}/+'

    def _get_start_recording_topic(self, video_ref: str):
        return f'camera/recording/{self.device_id}/start/{video_ref}-0'

    def _get_video_ack_topic(self, split_number: Optional[int] = None) -> str:
        """"
        When a video is created, the camera publish on this topic.
        The last parameter is the video_ref.
        It creates a file when:
        - split
        - end
        Start is a special case and it doesn't publish on this topic.
        """
        if split_number is None:
            return f'motion/video/{self.device_id}/+'

        return f'motion/video/{self.device_id}/{self.video_ref}-{split_number}'

    def _get_split_topic(self, video_ref: str, split_number: int) -> str:
        return f'camera/recording/{self.device_id}/split/{video_ref}-{split_number}'

    def _start_camera(self) -> None:
        self.client.publish(f'status/camera_manager/{self.device_id}', payload='{"status": "true", "data": {}}', qos=2)

    def _split_camera_video(self, split_number: int) -> None:
        topic = self._get_split_topic(self.video_ref, split_number)
        self.client.publish(topic)

    def _stop_camera_video(self, split_number: int) -> None:
        topic = f'camera/recording/{self.device_id}/end/{self.video_ref}-{split_number}'
        self.client.publish(topic)

    def on_connected_camera(self, _client, _userdata, msg) -> None:
        LOGGER.info("on_connected_camera")
        LOGGER.info(msg)
        start_topic = self._get_start_recording_topic(self.video_ref)
        # let the camera recording stuff to connect.
        # as of today I don't have any feedback on it.
        time.sleep(3)
        self.client.publish(start_topic, qos=2)

    def _assert_file_exists(self) -> None:
        if self.split_number == 0:
            expected_video_path = os.path.join(self.base_video_path, f'{self.video_ref}-0-before.h264')
            self.assertIsFile(expected_video_path)

            expected_video_path = os.path.join(self.base_video_path, f'{self.video_ref}-0.h264')
            self.assertIsFile(expected_video_path)
        else:
            expected_video_path = os.path.join(self.base_video_path, f'{self.video_ref}-{self.split_number}.h264')
            self.assertIsFile(expected_video_path)

    def on_ack_start_recording(self,  _client, _userdata, msg) -> None:
        LOGGER.info("on_ack_start_recording")
        LOGGER.info(msg)

        self._assert_file_exists()

        # ask to split
        self.split_number = self.split_number +1
        self._split_camera_video(split_number=self.split_number)

    def on_ack_first_video(self, _client, _userdata, msg) -> None:
        LOGGER.info("on_ack_first_video")
        # todo: check if file is on the disk.
        # if it's the first split, split again.
        # else (second), stop the record.
        #self.client.publish()
        self._assert_file_exists()

        self.split_number = self.split_number +1
        self._split_camera_video(split_number=self.split_number)

    def on_ack_second_video(self, _client, _userdata, msg) -> None:
        LOGGER.info("on_ack_second_video")

        self._assert_file_exists()
        self._stop_camera_video(split_number=self.split_number)

    def on_ack_end_video(self, _client, _userdata, msg) -> None:
        LOGGER.info("on_ack_end_video")
        self._assert_file_exists()
        self.client.disconnect()


    def test_start_record(self):
        LOGGER.info('test_start_record')
        start_ack_topic = self._get_start_ack_topic(self.video_ref)
        ack_video_topic = self._get_video_ack_topic()

        camera_connected_topic = self._get_camera_connected_topic()

        self.client.connect(self.hostname, self.port)

        self.client.subscribe(camera_connected_topic)
        self.client.message_callback_add(camera_connected_topic, self.on_connected_camera)

        self.client.subscribe(start_ack_topic)
        self.client.message_callback_add(start_ack_topic, self.on_ack_start_recording)

        self.client.subscribe(ack_video_topic)
        first_topic = self._get_video_ack_topic(split_number=0)
        LOGGER.info(f'add callback on {first_topic}')
        self.client.message_callback_add(first_topic, self.on_ack_first_video)
        self.client.message_callback_add(self._get_video_ack_topic(split_number=1), self.on_ack_second_video)
        self.client.message_callback_add(self._get_video_ack_topic(split_number=2), self.on_ack_end_video)

        self._start_camera()
        LOGGER.info("start mqtt loop")
        self.client.loop_forever()

