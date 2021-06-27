
from camera.camera_recording import CameraRecording, NoCameraRecording
from camera.camera_record import DumbCameraRecorder
from unittest.mock import Mock, patch
from service_manager.run_listen_frame import ConnectedDevices
from unittest.case import TestCase


class ConnectedDevicesTestCase(TestCase):
    def setUp(self) -> None:
        self.device_id = 'fake_device_id'
        self.mqtt_mock = Mock()
        self.connected_devices = ConnectedDevices(self.mqtt_mock)

    @patch('service_manager.run_listen_frame.camera_object_detection_factory')
    def test_factory_with_video_support(self, factory_mock):
        self.connected_devices.add(self.device_id, True)
        factory_mock.assert_called_once()
        
        args = factory_mock.call_args_list[0][0]
        self.assertIsInstance(args[1], CameraRecording)

    @patch('service_manager.run_listen_frame.camera_object_detection_factory')
    def test_factory_without_video_support(self, factory_mock):
        self.connected_devices.add(self.device_id, False)
        factory_mock.assert_called_once()
        
        args = factory_mock.call_args_list[0][0]
        self.assertIsInstance(args[1], NoCameraRecording)

