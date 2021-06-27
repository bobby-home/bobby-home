from camera.messaging import CameraData
from unittest.mock import Mock
from django.test import TestCase

from alarm.messaging import AlarmMessaging
from utils.mqtt.mqtt_status import MqttJsonStatus


class AlarmMessagingTestCase(TestCase):
    def setUp(self) -> None:
        self.device_id = '123456'
        self.device_type = 'pi0'
        self.mqtt_mock = Mock()
        self.speaker_messaging = Mock()
        self.camera_messaging = Mock()
        self.json_status = MqttJsonStatus(self.mqtt_mock)

        self.alarm = AlarmMessaging(self.json_status, self.speaker_messaging, self.camera_messaging)

    def test_synchronize_sound(self):
        self.alarm.publish_alarm_status(self.device_id, self.device_type, False)
        self.speaker_messaging.publish_speaker_status.assert_called_once_with(self.device_id, False)

    def test_no_synchronize_sound(self):
        self.alarm.publish_alarm_status(self.device_id, self.device_type, True)
        self.speaker_messaging.publish_speaker_status.assert_not_called()

    def test_camera_publish_true_status(self):
        data = CameraData(to_analyze=True, stream=None, video_spport=None)
        self.alarm.publish_alarm_status(self.device_id, self.device_type, True)
        self.camera_messaging.publish_status.assert_called_once_with(self.device_id, True, data)

    def test_camera_publish_false_status(self):
        data = CameraData(to_analyze=False, stream=None, video_spport=None)
        self.alarm.publish_alarm_status(self.device_id, self.device_type, False)
        self.camera_messaging.publish_status.assert_called_once_with(self.device_id, False, data)

    def test_camera_publish_esp_edge_case(self):
        data = CameraData(to_analyze=True, stream=None, video_spport=False)
        self.alarm.publish_alarm_status(self.device_id, 'esp32cam', True)
        self.camera_messaging.publish_status.assert_called_once_with(self.device_id, True, data)


