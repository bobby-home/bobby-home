from unittest.mock import Mock, patch

from django.test import TestCase

from devices.factories import DeviceFactory
from mqtt_services.models import MqttServicesConnectionStatusLogs
from utils.mqtt.mqtt_status_handler import OnConnectedHandlerLog


class OnConnectedHandlerLogTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.service_name = 'test_service'
        self.device_id = '12345'
        self.mqtt = Mock()
        self.handler = OnConnectedHandlerLog(self.mqtt)

    def test_on_connect_database_record(self):
        self.handler.on_connect(self.service_name, self.device_id)

        logs = MqttServicesConnectionStatusLogs.objects.filter(device_id=self.device_id, service_name=self.service_name, status=True)
        self.assertTrue(logs.exists())

    def test_on_disconnect_database_record(self):
        self.handler.on_disconnect(self.service_name, self.device_id)

        logs = MqttServicesConnectionStatusLogs.objects.filter(device_id=self.device_id, service_name=self.service_name, status=False)
        self.assertTrue(logs.exists())

    def test_call_is_status_exists_and_task_call(self):
        model_mock = Mock()

        with patch('alarm.business.alarm.is_status_exists') as is_status_exists, patch('mqtt_services.tasks.mqtt_status_does_not_match_database') as mock_task:
            is_status_exists.return_value = False
            handler = OnConnectedHandlerLog(self.mqtt, model_mock)

            handler.on_connect(self.service_name, self.device.device_id)
            is_status_exists.assert_called_once_with(model_mock, self.device.device_id, True)

            kwargs = {
                'device_id': self.device.device_id,
                'received_status': True,
                'service_name': self.service_name,
            }

            mock_task.apply_async.assert_called_once_with(kwargs=kwargs)

        with patch('alarm.business.alarm.is_status_exists') as is_status_exists, patch('mqtt_services.tasks.mqtt_status_does_not_match_database') as mock_task:
            is_status_exists.return_value = True
            handler = OnConnectedHandlerLog(self.mqtt, model_mock)

            handler.on_disconnect(self.service_name, self.device.device_id)
            is_status_exists.assert_called_once_with(model_mock, self.device.device_id, False)
            mock_task.apply_async.assert_not_called()
