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
