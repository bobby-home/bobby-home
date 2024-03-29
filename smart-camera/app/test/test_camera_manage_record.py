from dataclasses import dataclass
from uuid import uuid4
from camera.pivideostream import PiVideoStream
from mqtt.mqtt_client import MqttClient
from camera.manage_record import Command, ManageRecord
from unittest.case import TestCase
from unittest.mock import Mock

@dataclass
class FakeMqttMessage:
    topic: str


class CameraManageRecordTestCase(TestCase):
    def setUp(self) -> None:
        self.mqtt_mock = Mock(spec_set=MqttClient)
        self.video_mock = Mock(spec_set=PiVideoStream)
        self.device_id = str(uuid4())

        self.video_ref_uuid = str(uuid4())
        self.video_ref = f'{self.video_ref_uuid}-1'

        self.manage_record = ManageRecord(self.mqtt_mock, self.device_id, self.video_mock)

        self.start_message = FakeMqttMessage(topic=f'camera/recording/{self.device_id}/start/{self.video_ref}')
        self.end_message = FakeMqttMessage(topic=f'camera/recording/{self.device_id}/end/{self.video_ref}')
        self.split_message = FakeMqttMessage(topic=f'camera/recording/{self.device_id}/split/{self.video_ref}')

        self.video_mock.start_recording.return_value = True
        self.video_mock.stop_recording.return_value = True
        self.video_mock.split_recording.return_value = True

        return super().setUp()

    def _check_ack(self):
        self.mqtt_mock.client.publish.assert_called_once_with(f'motion/video/{self.device_id}/{self.video_ref}', qos=1)

    def _check_ack_start(self):
        self.mqtt_mock.client.publish.assert_called_once_with(f'ack/video/started/{self.device_id}/{self.video_ref}', qos=2)

    def _check_no_ack(self):
        self.mqtt_mock.client.publish.assert_not_called()

    def _check_ack_split(self):
        self.mqtt_mock.client.publish.assert_called_once_with(f'motion/video/{self.device_id}/{self.video_ref_uuid}-0', qos=1)

    def test_extract_data_from_topic(self):
        print(' MKJHESRFGKJLMESGKJDRFHGLKJRFDGJKDRHGJKRFH')
        topic = self.manage_record._extract_data_from_topic(f'camera/recording/{self.device_id}/split/{self.video_ref}')
        expected_command = Command(
            action='split', video_ref=self.video_ref, split_number=1, event_ref=self.video_ref_uuid
        )
        self.assertEqual(topic, expected_command)
        print(topic)

    def test_start_recording(self):
        self.manage_record._on_record(None, None, self.start_message)
        self.video_mock.start_recording.assert_called_once_with(self.video_ref)
        self._check_ack_start()

    def test_end_recording(self):
        self.manage_record._on_record(None, None, self.end_message)
        self.video_mock.stop_recording.assert_called_once_with()
        self._check_ack()

    def test_split_recording(self):
        self.manage_record._on_record(None, None, self.split_message)
        self.video_mock.split_recording.assert_called_once_with(self.video_ref)
        self._check_ack_split()

    def test_end_recording_no_ack(self):
        self.video_mock.stop_recording.return_value = False
        self.manage_record._on_record(None, None, self.end_message)
        self._check_no_ack()

    def test_split_recording_no_ack(self):
        self.video_mock.split_recording.return_value = False
        self.manage_record._on_record(None, None, self.split_message)
        self._check_no_ack()

    def test_no_crash_invalid_message(self):
        """
        This method is called when it receives mqtt message.
        If the message is wrong, it should not raise any exception, it would cause the process to crash,
        thus loosing part of video.
        """
        message = FakeMqttMessage(topic=f'camera/recording/wrongthing')
        self.manage_record._on_record(None, None, message)
        self._check_no_ack()
        message = FakeMqttMessage(topic=f'blabla')
        self.manage_record._on_record(None, None, message)
        self._check_no_ack()
