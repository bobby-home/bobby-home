from unittest import TestCase
from unittest.mock import Mock
from service_manager.run_listen_frame import RunListenFrame 


class RunListenFrameTestCase(TestCase):

    def setUp(self) -> None:
        self.connected_devices = Mock()
        self.runnable = RunListenFrame(self.connected_devices)
        self.device_id = 'some_device_id'
        self.payload = {'to_analyze': True}

    def test_add_device(self):
        self.connected_devices.has.return_value = False

        self.runnable.run(self.device_id, True, self.payload) 
        self.connected_devices.add.assert_called_once_with(self.device_id, True)

        self.connected_devices.has.return_value = True
        self.runnable.run(self.device_id, True, self.payload) 

    def test_remove_device(self):
        self.runnable.run(self.device_id, False, self.payload) 
        self.connected_devices.remove.assert_called_once_with(self.device_id)

    def test_dont_add_device(self):
        self.connected_devices.has.return_value = False

        self.runnable.run(self.device_id, True, {'to_analyze': False}) 
        self.connected_devices.add.assert_not_called()

    def test_add_with_video_support_param(self):
        self.connected_devices.has.return_value = False

        self.runnable.run(self.device_id, True, {'to_analyze': True, 'video_support': False}) 
        self.connected_devices.add.assert_called_once_with(self.device_id, False)
