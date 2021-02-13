import struct
from unittest import TestCase
from unittest.mock import Mock

from mqtt.mqtt_manage_runnable import MqttManageRunnable

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MqttManageRunnableTestCase(TestCase):
    def setUp(self) -> None:
        self.host_device_id = 'host device id'
        self.device_id = 'some device id'
        self.mqtt_mock = Mock()
        self.runnable_mock = Mock()

    def test_run_multi_device(self):
        manager = MqttManageRunnable(self.host_device_id, 'listen_frame', self.mqtt_mock, self.runnable_mock, False, True)

        mqtt_msg = {
            'topic': f'camera/status/{self.device_id}',
            'payload': struct.pack('?', True)
        }

        manager._switch_on_or_off(None, None, DotDict(mqtt_msg))

        self.runnable_mock.run.assert_called_once_with(self.device_id, True, None)

        self.runnable_mock.reset_mock()

        mqtt_msg = {
            'topic': f'camera/status/{self.device_id}',
            'payload': struct.pack('?', False)
        }

        manager._switch_on_or_off(None, None, DotDict(mqtt_msg))
        self.runnable_mock.run.assert_called_once_with(self.device_id, False)

    def test_run_host(self):
        manager = MqttManageRunnable(self.host_device_id, 'listen_frame', self.mqtt_mock, self.runnable_mock, False, False)

        mqtt_msg = {
            'topic': f'camera/status/{self.device_id}',
            'payload': struct.pack('?', True)
        }

        manager._switch_on_or_off(None, None, DotDict(mqtt_msg))

        self.runnable_mock.run.assert_called_once_with(self.host_device_id, True, None)
