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
        self.device_id = "device_id_uuid"
        self.video_ref = "video_ref_uuid"
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

    def _check_no_ack(self):
        self.mqtt_mock.client.publish.assert_not_called()

    def test_start_recording(self):
        self.manage_record._on_record(None, None, self.start_message)
        self.video_mock.start_recording.assert_called_once_with(self.video_ref)
        self._check_no_ack()

    def test_end_recording(self):
        self.manage_record._on_record(None, None, self.end_message)
        self.video_mock.stop_recording.assert_called_once_with()
        self._check_ack()

    def test_split_recording(self):
        self.manage_record._on_record(None, None, self.split_message)
        self.video_mock.split_recording.assert_called_once_with(self.video_ref)
        self._check_ack()
