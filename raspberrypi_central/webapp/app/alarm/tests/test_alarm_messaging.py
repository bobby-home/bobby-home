from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from alarm.messaging import AlarmMessaging
from utils.mqtt.mqtt_status import MqttJsonStatus


class AlarmMessagingTestCase(TestCase):
    def setUp(self) -> None:
        self.device_id = '123456'
        self.verify_service_status = Mock()
        self.mqtt_mock = Mock()
        self.speaker_messaging = Mock()
        self.json_status = MqttJsonStatus(self.mqtt_mock)

        self.alarm = AlarmMessaging(self.json_status, self.speaker_messaging, self.verify_service_status)

    def test_synchronize_sound(self):
        self.alarm.publish_alarm_status(self.device_id, False)
        self.speaker_messaging.publish_speaker_status.assert_called_once_with(self.device_id, False)

    def test_no_synchronize_sound(self):
        self.alarm.publish_alarm_status(self.device_id, True)
        self.speaker_messaging.publish_speaker_status.assert_not_called()

    @freeze_time("2020-12-21 03:21:00")
    def test_verify_service_status(self):
        self.alarm.publish_alarm_status(self.device_id, False)

        kwargs = {
            'device_id': self.device_id,
            'service_name': 'object_detection',
            'status': False,
            'since_time': timezone.now()
        }

        self.verify_service_status.apply_async.assert_called_once_with(kwargs=kwargs, countdown=5)
