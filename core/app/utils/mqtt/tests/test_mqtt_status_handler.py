import dataclasses
from dataclasses import dataclass
import unittest
from unittest.case import skip
from unittest.mock import Mock, patch

from django.test import TestCase
from alarm.models import AlarmStatus
from devices.factories import DeviceFactory
from mqtt_services.models import MqttServicesConnectionStatusLogs
from utils.mqtt import MqttMessage
from utils.mqtt.mqtt_status_handler import OnConnectedHandlerLog, OnConnectedVerifyStatusHandler, OnStatus, service_status_topic 
import utils.date as dt_utils


class ServiceStatusTopicTestCase(unittest.TestCase):
    def test_split_camera_topic(self):
        service = 'object_detection'
        device_id = 'deviceid'

        response = service_status_topic(f'connected/{service}/{device_id}')
        self.assertEqual(dataclasses.asdict(response), {
            'service': service,
            'device_id': device_id,
        })

        with self.assertRaises(ValueError) as err:
            service_status_topic(f'{type}-{service}')


class OnStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.service_name = 'some_service_name'
        self.device_id = self.device.device_id
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


class OnConnectedVerifyTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id: str = self.device.device_id
        self.service_name = 'test_service'

        self.alarm_status = AlarmStatus(device=self.device)
        self.handler = OnConnectedVerifyStatusHandler(AlarmStatus)

    @patch('mqtt_services.tasks.mqtt_status_does_not_match_database')
    def test_disconnect_running_false(self, mock_task):
        AlarmStatus.objects.create(device=self.device, running=False)

        self.handler.on_disconnect(self.service_name, self.device_id)
        mock_task.apply_async.assert_not_called()

    @patch('mqtt_services.tasks.mqtt_status_does_not_match_database')
    def test_disconnect_running_true(self, mock_task):
        AlarmStatus.objects.create(device=self.device, running=False)

        self.handler.on_connect(self.service_name, self.device_id)

        kwargs = {
            'device_id': self.device.device_id,
            'received_status': True,
            'service_name': self.service_name,
        }

        mock_task.apply_async.assert_called_once_with(kwargs=kwargs)

    @patch('mqtt_services.tasks.mqtt_status_does_not_match_database')
    def test_connect_running_true(self, mock_task):
        AlarmStatus.objects.create(running=True, device=self.device)

        self.handler.on_connect(self.service_name, self.device_id)
        mock_task.apply_async.assert_not_called()

    @patch('mqtt_services.tasks.mqtt_status_does_not_match_database')
    def test_connect_running_false(self, mock_task):
        AlarmStatus.objects.create(running=False, device=self.device)

        self.handler.on_connect(self.service_name, self.device_id)
        kwargs = {
            'device_id': self.device.device_id,
            'received_status': True,
            'service_name': self.service_name,
        }

        mock_task.apply_async.assert_called_once_with(kwargs=kwargs)


class OnConnectedHandlerLogTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.service_name = 'test_service'
        self.device_id: str = self.device.device_id
        self.mqtt = Mock()
        self.handler = OnConnectedHandlerLog()

    def test_on_connect_database_record(self):
        self.handler.on_connect(self.service_name, self.device_id)

        logs = MqttServicesConnectionStatusLogs.objects.filter(device_id=self.device_id, service_name=self.service_name, status=True)
        self.assertTrue(logs.exists())

    def test_on_disconnect_database_record(self):
        self.handler.on_disconnect(self.service_name, self.device_id)

        logs = MqttServicesConnectionStatusLogs.objects.filter(device_id=self.device_id, service_name=self.service_name, status=False)
        self.assertTrue(logs.exists())

