from alarm.models import Ping
from alarm.business.alarm_ping import register_ping
from django.test import TestCase


class RegisterTestPing(TestCase):
    def setUp(self) -> None:
        self._device_id = 'id5'
        self._service_name = 'service_name'

    def test_register_ping_create(self):
        register_ping(self._device_id, self._service_name)
        pings = Ping.objects.filter(device_id=self._device_id)
        self.assertEqual(1, len(pings))

    def test_register_update(self):
        Ping.objects.create(
                device_id=self._device_id,
                service_name=self._service_name,
                consecutive_failures=2,
        )
        
        register_ping(self._device_id, self._service_name)
        pings = Ping.objects.filter(device_id=self._device_id)

        self.assertEqual(1, len(pings), 'it should update ping, not create a new one')
        ping = pings[0]
        self.assertEqual(0, ping.consecutive_failures, 'it should reset consecutive_failures when new ping is registered')
        self.assertEqual(2, ping.failures, 'it should add consecutive_failures to failures')

