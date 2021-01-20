from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from alarm.models import AlarmStatus
from devices.factories import DeviceFactory
from alarm.business.alarm import is_status_exists
from mqtt_services.models import MqttServicesConnectionStatusLogs
from mqtt_services.business.mqtt_services import is_in_status_since


class HealthTestCase(TransactionTestCase):
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
