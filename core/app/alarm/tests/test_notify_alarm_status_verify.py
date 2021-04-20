from alarm.mqtt import MqttServices, CameraMqttServices
from django.test import TestCase
from unittest.mock import call, patch

from django.utils import timezone
from freezegun import freeze_time

from devices.factories import DeviceFactory
from alarm.use_cases.checks import verify_services_status


class NotifyAlarmStatusVerify(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id

    @freeze_time("2020-12-21 03:21:00")
    @patch('mqtt_services.tasks.verify_service_status')
    def test_verify_service_status(self, verify_service_status):
        def _test(status: bool):
            verify_services_status(self.device_id, status, False)
            
            kwargs = {
                'device_id': self.device_id,
                'service_name': MqttServices.OBJECT_DETECTION.value,
                'status': status,
                'since_time': timezone.now()
            }

            kwargs2 = {
                'device_id': self.device_id,
                'service_name': CameraMqttServices.CAMERA.value,
                'status': status,
                'since_time': timezone.now()
            }
            
            calls = [
                call(kwargs=kwargs, countdown=15),
                call(kwargs=kwargs2, countdown=15),
            ]
            verify_service_status.apply_async.assert_has_calls(calls)

        _test(False)
        verify_service_status.reset_mock()
        _test(True)

