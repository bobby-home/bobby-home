from unittest import TestCase
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
                'service_name': 'object_detection',
                'status': status,
                'since_time': timezone.now()
            }

            verify_service_status.apply_async.assert_called_once_with(kwargs=kwargs, countdown=15)

        _test(False)
        verify_service_status.reset_mock()
        _test(True)

    @freeze_time("2020-12-21 03:21:00")
    @patch('mqtt_services.tasks.verify_service_status')
    def test_verify_service_status_dumb_alarm(self, verify_service_status):
        verify_services_status(self.device_id, False, True)

        # kwargs_object_detection = {
        #     'device_id': self.device_id,
        #     'service_name': 'object_detection',
        #     'status': False,
        #     'since_time': timezone.now()
        # }

        kwargs_dumb_camera = {
            'device_id': self.device_id,
            'service_name': 'dumb_camera',
            'status': False,
            'since_time': timezone.now()
        }

        verify_service_status.apply_async.assert_has_calls([
            # call(kwargs=kwargs_object_detection, countdown=15),
            call(kwargs=kwargs_dumb_camera, countdown=15),
        ])
