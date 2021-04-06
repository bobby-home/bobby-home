from datetime import timedelta

from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from freezegun import freeze_time

from alarm.models import AlarmStatus
from devices.factories import DeviceFactory
from alarm.business.alarm import is_status_exists
from mqtt_services.models import MqttServicesConnectionStatusLogs
from mqtt_services.business.mqtt_services import is_in_status_since, is_last_status
from mqtt_services.tasks import cleanup


class IsLastStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.service_name = 'camera'

    def test_is_is_last_status(self):

        # without any records it should be False.
        self.assertFalse(is_last_status(self.device.device_id, self.service_name, True))
        self.assertFalse(is_last_status(self.device.device_id, self.service_name, False))

        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=True,
        )
        self.assertFalse(is_last_status(self.device.device_id, self.service_name, False))
        self.assertTrue(is_last_status(self.device.device_id, self.service_name, True))

        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=False,
        )
        self.assertFalse(is_last_status(self.device.device_id, self.service_name, True))
        self.assertTrue(is_last_status(self.device.device_id, self.service_name, False))

class IsInStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.service_name = 'camera'
        self.now = timezone.now()

    def test_is_in_status_since(self):
        now = timezone.now()
        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=True,
        )

        self.assertTrue(
            is_in_status_since(self.device.device_id, self.service_name, True, now)
        )

        self.assertFalse(
            is_in_status_since(self.device.device_id, self.service_name, False, now)
        )

        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=False,
        )

        self.assertFalse(
            is_in_status_since(self.device.device_id, self.service_name, True, now),
            'If the service turns on but turn off before the check, it should be false.'
        )

    def test_is_in_status_since_false_true(self):
        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=False,
        )
        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=True,
        )

        self.assertTrue(
            is_in_status_since(self.device.device_id, self.service_name, True, self.now)
        )

    def test_is_in_status_since_true_false(self):
        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=True,
        )
        MqttServicesConnectionStatusLogs.objects.create(
            device_id=self.device.device_id, service_name=self.service_name, status=False,
        )

        self.assertFalse(
            is_in_status_since(self.device.device_id, self.service_name, True, self.now)
        )

    def test_is_status_exists(self):
        other_device = DeviceFactory()

        AlarmStatus.objects.create(device=self.device, running=True)


        self.assertTrue(
            is_status_exists(AlarmStatus, device_id=self.device.device_id, running=True)
        )

        self.assertFalse(
            is_status_exists(AlarmStatus, device_id=self.device.device_id, running=False)
        )

        self.assertFalse(
            is_status_exists(AlarmStatus, device_id=other_device.device_id, running=True)
        )

class CleanTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.service_name = 'some_service'

        with freeze_time(timezone.now() - timedelta(days=2)):
            self.to_delete = [
                MqttServicesConnectionStatusLogs.objects.create(
                    device_id=self.device.device_id, service_name=self.service_name, status=False,
                ),
                MqttServicesConnectionStatusLogs.objects.create(
                    device_id=self.device.device_id, service_name=self.service_name, status=True
                ),
            ]

        with freeze_time(timezone.now() - timedelta(minutes=50)):
            self.to_keep = [
                MqttServicesConnectionStatusLogs.objects.create(
                    device_id=self.device.device_id, service_name=self.service_name, status=True,
                ),
                MqttServicesConnectionStatusLogs.objects.create(
                    device_id=self.device.device_id, service_name=self.service_name, status=False,
                ),
            ]

    def test_clean(self):
        cleanup()
        logs = MqttServicesConnectionStatusLogs.objects.all()
        self.assertEqual(2, len(logs))

        for i, log in enumerate(logs):
            self.assertEqual(log, self.to_keep[i])
