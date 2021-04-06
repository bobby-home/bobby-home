import json
import struct
from unittest import TestCase
from unittest.mock import Mock

from utils.mqtt.mqtt_status import MqttBooleanStatus, MqttJsonStatus


class MqttBooleanStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.mqtt_client_mock = Mock()
        self.c = MqttBooleanStatus(self.mqtt_client_mock)
        self.topic = 'connected/service/device_id'

    def test_call_publish_true(self):
        self.c.publish('connected/service/device_id', True)
        self.mqtt_client_mock.publish.assert_called_once_with(self.topic, struct.pack('?', True), qos=1, retain=True)

    def test_call_publish_false(self):
        self.c.publish('connected/service/device_id', False)
        self.mqtt_client_mock.publish.assert_called_once_with(self.topic, struct.pack('?', False), qos=1, retain=True)


class MqttJsonStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.mqtt_client_mock = Mock()
        self.c = MqttJsonStatus(self.mqtt_client_mock)
        self.topic = 'connected/service/device_id'

    def test_call_publish(self):
        data = {'is_dumb': True, 'blabla': 3.14444}

        self.c.publish(self.topic, True, data)

        expected_payload = {
            'status': True,
            'data': data
        }

        self.mqtt_client_mock.publish.assert_called_once_with(self.topic, json.dumps(expected_payload), qos=1, retain=True)
