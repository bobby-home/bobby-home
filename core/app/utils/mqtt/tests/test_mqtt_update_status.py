from alarm.mqtt.on_status_update import OnUpdateStatus, UpdateStatusPayload
from unittest.mock import ANY, Mock
from utils.mqtt.mqtt_data import MqttMessage, MqttTopicSubscriptionJson
from utils.mqtt.mqtt_update_status import OnUpdate, OnUpdateStatusHandler, UpdateStatusDescriptor, on_updates
from devices.factories import DeviceFactory
from django.test.testcases import TestCase
import utils.date as dt_utils
from alarm.mqtt.mqtt_updates import MqttUpdates


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
        self.handler_mock.on_toggle_device.assert_not_called()
        self.handler_mock.on_update_all.assert_not_called()
        self.handler_mock.on_update_device.assert_called_once_with(expected_payload, self.device_id)

    def test_on_update_toggle(self):
        topic = f'update/{self.service_name}/{self.device_id}'

        payload = {
            'status': 'toggle'
        }

        message = MqttMessage(
            topic,
            payload,
            self.qos,
            self.retain,
            topic,
            self.timestamp,
        )

        expected_payload = UpdateStatusPayload(**message.payload)

        self.on_update.on_update(message)
        self.handler_mock.on_toggle_device.assert_called_once_with(expected_payload, self.device_id)
        self.handler_mock.on_update_all.assert_not_called()
        self.handler_mock.on_update_device.assert_not_called()


    def test_on_update_toggle_raise(self):
        topic = f'update/{self.service_name}'

        payload = {
            'status': 'toggle'
        }

        message = MqttMessage(
            topic,
            payload,
            self.qos,
            self.retain,
            topic,
            self.timestamp,
        )

        with self.assertRaises(ValueError) as _context:
            self.on_update.on_update(message)
        self.handler_mock.on_update_all.assert_not_called()
        self.handler_mock.on_toggle_device.assert_not_called()
        self.handler_mock.on_update_device.assert_not_called()

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
        self.handler_mock.on_toggle_device.assert_not_called()


class OnUpdateMqttSubscribeTestCase(TestCase):
    def setUp(self) -> None:
        self.mqtt = Mock()
        
        self.updates = (
            UpdateStatusDescriptor(
                name=MqttUpdates.ALARM.value,
                on_update=OnUpdateStatus,
                payload_type=UpdateStatusPayload
            ),
        ) 

    def test_mqtt_subscribe(self):
        call_param = []
        for service in self.updates:
            p = MqttTopicSubscriptionJson(
                topic=f'update/{service.name}/+',
                _callback=ANY,
                qos=1
            )
            call_param.append(p)

        on_updates(self.mqtt, self.updates)
        self.mqtt.add_subscribe.assert_called_once_with(call_param)
