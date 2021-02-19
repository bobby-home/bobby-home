from unittest.mock import Mock, patch

from django.test import TestCase

from alarm.communication.on_connected_services import OnConnectedObjectDetectionHandler
from alarm.factories import AlarmStatusFactory
from devices.factories import DeviceFactory


class OnConnectedServices(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.alarm_status = AlarmStatusFactory(device=self.device)
        self.mqtt = Mock()

    def test_on_connect_send_data(self):
        handler = OnConnectedObjectDetectionHandler(self.mqtt)

        with patch('alarm.communication.out_alarm.notify_alarm_status_factory') as notify_alarm_status_factory:
            notify = Mock()
            notify_alarm_status_factory.return_value = notify

            handler.on_connect('serivce_name', self.device.device_id)
            notify.publish_device_connected.assert_called_once_with(self.device.device_id)

    def test_on_connect_close_motions(self):
        handler = OnConnectedObjectDetectionHandler(self.mqtt)

        with patch('camera.business.camera_motion.close_unclosed_camera_motions') as camera_motion:
            handler.on_connect('serivce_name', self.device.device_id)

            camera_motion.assert_called_once_with(self.device.device_id)

    def test_on_disconnect_close_motion(self):
        handler = OnConnectedObjectDetectionHandler(self.mqtt)

        with patch('camera.business.camera_motion.close_unclosed_camera_motions') as camera_motion:
            handler.on_disconnect('serivce_name', self.device.device_id)

            camera_motion.assert_called_once_with(self.device.device_id)
