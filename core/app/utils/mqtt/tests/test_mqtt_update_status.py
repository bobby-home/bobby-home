
from alarm.mqtt.on_status_update import UpdateStatusPayload
from unittest.mock import Mock
from utils.mqtt.mqtt_data import MqttMessage
from utils.mqtt.mqtt_update_status import OnUpdate
from devices.factories import DeviceFactory
from django.test.testcases import TestCase
import utils.date as dt_utils


class MqttUpdateStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.service_name = 'some_service_name'
        self.device_id = self.device.device_id
        self.retain = False
        self.qos = 1

        self.timestamp = dt_utils.utcnow()

        self.handler_mock = Mock()
        self.on_update = OnUpdate(self.handler_mock, payload=UpdateStatusPayload)

    def test_on_update_device(self):
        topic = f'update/{self.service_name}/{self.device_id}'

        payload = {
            'status': 'off'
        }

        message = MqttMessage(
            topic,
            payload,
            self.qos,
            self.retain,
            topic,
            self.timestamp,
        )

        self.on_update.on_update(message)

        expected_payload = UpdateStatusPayload(**message.payload)
        self.handler_mock.on_update_all.assert_not_called()
        self.handler_mock.on_update_device.assert_called_once_with(expected_payload, self.device_id)

    def test_on_update_all(self):
        topic = f'update/{self.service_name}'

        payload = {
            'status': 'off'
        }

        message = MqttMessage(
            topic,
            payload,
            self.qos,
            self.retain,
            topic,
            self.timestamp,
        )

        self.on_update.on_update(message)

        expected_payload = UpdateStatusPayload(**message.payload)
        self.handler_mock.on_update_all.assert_called_once_with(expected_payload)
        self.handler_mock.on_update_device.assert_not_called()
