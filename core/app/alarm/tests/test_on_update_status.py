from alarm.models import AlarmStatus
from alarm.factories import AlarmStatusFactory
from unittest.mock import patch
from django.test import TestCase
from alarm.mqtt.on_status_update import OnUpdateStatus, UpdateStatusPayload


class OnUpdateStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.update = OnUpdateStatus()

    @patch('alarm.mqtt.on_status_update.AlarmChangeStatus')
    def test_toggle(self, alarm_change_status_mock):
        alarm_status = AlarmStatusFactory()
        device_id = alarm_status.device.device_id

        data_payload = UpdateStatusPayload(status='toggle')
        self.update.on_toggle_device(data_payload, device_id=device_id)

        alarm_change_status_mock.reverse_status.assert_called_once_with(alarm_status.pk, force=False)


    @patch('alarm.mqtt.on_status_update.AlarmChangeStatus')
    def test_specific_device(self, alarm_change_status_mock):
        self.alarm_status = AlarmStatusFactory()
        device_id = self.alarm_status.device.device_id
        data_payload = UpdateStatusPayload(status='on', force='on')
        self.update.on_update_device(data_payload, device_id=device_id)
        
        s = AlarmStatus.objects.get(device__device_id=device_id)
        s.running = True
        
        alarm_change_status_mock.save_status.assert_called_once_with(s, force=True)
        alarm_change_status_mock.all_change_status.assert_not_called()
        

    @patch('alarm.mqtt.on_status_update.AlarmChangeStatus')
    def test_all_device(self, alarm_change_status_mock):
        data_payload = UpdateStatusPayload(status='on', force='on')
        self.update.on_update_all(data_payload)
        alarm_change_status_mock.all_change_status.assert_called_once_with(status=True, force=True)
        alarm_change_status_mock.save_status.assert_not_called()
