from unittest.mock import Mock, patch

from django.test import TestCase

from devices.factories import DeviceFactory
from mqtt_services.models import MqttServicesConnectionStatusLogs
from utils.mqtt import MqttMessage
from utils.mqtt.mqtt_status_handler import OnConnectedHandlerLog, OnStatus, split_camera_topic
import utils.date as dt_utils


class SplitCameraTopicTestCase(TestCase):
    def test_split_camera_topic(self):
        type = 'connected'
        service = 'object_detection'
        device_id = 'some device id'

        response = split_camera_topic(f'{type}/{service}/{device_id}')
        self.assertEqual(response, {
            'type': type,
            'service': service,
            'device_id': device_id,
        })

        with self.assertRaises(ValueError) as err:
            split_camera_topic(f'{type}-{service}')


class OnStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.service_name = 'some_service_name'
        self.device_id = '1234567'
        self.topic = f'connected/{self.service_name}/{self.device_id}'
        self.retain = False
        self.qos = 1
        self.payload = True

        self.timestamp = dt_utils.utcnow()

    def test_on_connect_calls_connect(self):
        handler_mock = Mock()
        on_status = OnStatus(handler_mock)

        message = MqttMessage(
            self.topic,
            self.payload,
            self.qos,
            self.retain,
            self.topic,
            self.timestamp,
        )

        on_status.on_connected(message)
        handler_mock.on_connect.assert_called_once_with(self.service_name, self.device_id)
        handler_mock.on_disconnect.assert_not_called()

    def test_on_connect_calls_disconnect(self):
        message = MqttMessage(
            self.topic,
            False,
            self.qos,
            self.retain,
            self.topic,
            self.timestamp,
        )

        handler_mock = Mock()
        on_status = OnStatus(handler_mock)

        on_status.on_connected(message)
        handler_mock.on_disconnect.assert_called_once_with(self.service_name, self.device_id)
        handler_mock.on_connect.assert_not_called()


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
