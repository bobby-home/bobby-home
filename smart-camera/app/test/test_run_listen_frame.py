from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import ANY
from service_manager.run_listen_frame import RunListenFrame, ConnectedDevices


class RunListenFrameTestCase(TestCase):

    def setUp(self) -> None:
        self.connected_devices = Mock()
        self.runnable = RunListenFrame(self.connected_devices)
        self.device_id = 'some_device_id'
#
    def test_add_device(self):
        self.connected_devices.has.return_value = False

        self.runnable.run(self.device_id, True, {'is_dumb': True, 'rois': {'full': True}})
        self.connected_devices.add.assert_called_once_with(self.device_id, ANY)

        self.connected_devices.has.return_value = True
        self.runnable.run(self.device_id, True, {'is_dumb': True, 'rois': {'full': True}})

    def test_add_device_ignore_not_dumb(self):
        self.connected_devices.has.return_value = False

        self.runnable.run(self.device_id, True, {'is_dumb': False, 'rois': {'full': True}})
        self.connected_devices.assert_not_called()

    def test_remove_device(self):
        self.runnable.run(self.device_id, False, {'is_dumb': True, 'rois': {'full': True}})
        self.connected_devices.remove.assert_called_once_with(self.device_id)

    def test_remove_device_ignore_not_dumb(self):
        self.runnable.run(self.device_id, False, {'is_dumb': False, 'rois': {'full': True}})
        self.connected_devices.remove.assert_not_called()
