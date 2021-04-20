from unittest.mock import Mock
from django.test import TestCase

from alarm.messaging import AlarmMessaging
from utils.mqtt.mqtt_status import MqttJsonStatus


class AlarmMessagingTestCase(TestCase):
    def setUp(self) -> None:
        self.device_id = '123456'
        self.mqtt_mock = Mock()
        self.speaker_messaging = Mock()
        self.camera_messaging = Mock()
        self.json_status = MqttJsonStatus(self.mqtt_mock)

        self.alarm = AlarmMessaging(self.json_status, self.speaker_messaging, self.camera_messaging)

    def test_synchronize_sound(self):
        self.alarm.publish_alarm_status(self.device_id, False, False)
        self.speaker_messaging.publish_speaker_status.assert_called_once_with(self.device_id, False)

    def test_no_synchronize_sound(self):
        self.alarm.publish_alarm_status(self.device_id, True, False)
        self.speaker_messaging.publish_speaker_status.assert_not_called()
