from camera.messaging import CameraData
from unittest.mock import Mock
from django.test import TestCase

from alarm.messaging import AlarmMessaging
from utils.mqtt.mqtt_status import MqttJsonStatus


class AlarmMessagingTestCase(TestCase):
    def setUp(self) -> None:
        self.device_id = '123456'
        self.mqtt_mock = Mock()
        self.camera_messaging = Mock()
        self.json_status = MqttJsonStatus(self.mqtt_mock)

        self.alarm = AlarmMessaging(self.json_status, self.camera_messaging)

    def test_camera_publish_true_status(self):
        data = CameraData(to_analyze=True, stream=None)
        self.alarm.publish_alarm_status(self.device_id, True)
        self.camera_messaging.publish_status.assert_called_once_with(self.device_id, True, data)

    def test_camera_publish_false_status(self):
        data = CameraData(to_analyze=False, stream=None)
        self.alarm.publish_alarm_status(self.device_id, False)
        self.camera_messaging.publish_status.assert_called_once_with(self.device_id, False, data)

