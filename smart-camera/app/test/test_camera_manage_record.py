from dataclasses import dataclass
from camera.pivideostream import PiVideoStream
from mqtt.mqtt_client import MqttClient
from camera.manage_record import ManageRecord
from unittest.case import TestCase
from unittest.mock import Mock

@dataclass
class FakeMqttMessage:
    topic: str


class CameraManageRecordTestCase(TestCase):
    def setUp(self) -> None:
        self.mqtt_mock = Mock(spec_set=MqttClient)
        self.video_mock = Mock(spec_set=PiVideoStream)
        self.device_id = "some_uuid"
        self.video_ref = "event_ref"
        self.manage_record = ManageRecord(self.mqtt_mock, self.device_id, self.video_mock)

        self.start_message = FakeMqttMessage(topic=f'camera/recording/{self.device_id}/start/{self.video_ref}')
        self.end_message = FakeMqttMessage(topic=f'camera/recording/{self.device_id}/end')
        self.split_message = FakeMqttMessage(topic=f'camera/recording/{self.device_id}/split/{self.video_ref}')

        return super().setUp()

    def test_start_recording(self):
        self.manage_record._on_record(None, None, self.start_message)
        self.video_mock.start_recording.assert_called_once_with(self.video_ref)

    def test_end_recording(self):
        self.manage_record._on_record(None, None, self.end_message)
        self.video_mock.stop_recording.assert_called_once_with()

    def test_split_recording(self):
        self.manage_record._on_record(None, None, self.split_message)
        self.video_mock.split_recording.assert_called_once_with(self.video_ref)

