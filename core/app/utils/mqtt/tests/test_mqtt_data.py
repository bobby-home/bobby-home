import struct
from unittest import TestCase
from unittest.mock import Mock

from paho.mqtt.client import MQTTMessage
from utils.mqtt.mqtt_data import MqttTopicSubscriptionJson, MqttTopicSubscriptionBoolean, MqttMessage


class MqttTopicSubscriptionBooleanTestCase(TestCase):
    def setUp(self) -> None:
        self.service_name = 'some service'
        self.callback_mock = Mock()
        self.subscription = MqttTopicSubscriptionBoolean(f'connected/{self.service_name}/+', self.callback_mock)

    def test_call_unpacked_bool(self):
        self.subscription.callback(MqttMessage(
            f'connected/{self.service_name}',
            struct.pack('?', False),
            1,
            False,
        ))

        self.callback_mock.assert_called_once_with(MqttMessage(
            f'connected/{self.service_name}',
            False,
            1,
            False,
        ))

    def test_dont_call_wrong_payload(self):
        self.subscription.callback(MqttMessage(
            f'connected/{self.service_name}',
            'wrong payload',
            1,
            False,
        ))
        self.callback_mock.assert_not_called()

    def test_call_string_bool_true(self):
        self.subscription.callback(MqttMessage(
            f'connected/{self.service_name}',
            b"1",
            1,
            False,
        ))

        self.callback_mock.assert_called_once_with(MqttMessage(
            f'connected/{self.service_name}',
            True,
            1,
            False,
        ))

    def test_call_string_bool_false(self):
        self.subscription.callback(MqttMessage(
            f'connected/{self.service_name}',
            b"0",
            1,
            False,
        ))

        self.callback_mock.assert_called_once_with(MqttMessage(
            f'connected/{self.service_name}',
            False,
            1,
            False,
        ))

class MqttTopicSubscriptionJsonTestCase(TestCase):
    def setUp(self) -> None:
        self.service_name = 'some service'
        self.callback_mock = Mock()
        self.subscription = MqttTopicSubscriptionJson(f'connected/{self.service_name}/+', self.callback_mock)

    def test_call_json(self):
        expected_payload = {'is_dumb': 'yes'}

        self.subscription.callback(MqttMessage(
            f'connected/{self.service_name}',
            '{"is_dumb": "yes"}',
            1,
            False,
        ))
        self.callback_mock.assert_called_once_with(MqttMessage(
            f'connected/{self.service_name}',
            expected_payload,
            1,
            False,
        ))

    def test_dont_call_wrong_payload(self):
        self.subscription.callback(MqttMessage(
            f'connected/{self.service_name}',
            'wrong payload',
            1,
            False,
        ))
        self.callback_mock.assert_not_called()
