
from unittest.mock import patch
from alarm.integration.camera_motion import integration_camera_motion, integration_camera_no_more_motion
from devices.factories import DeviceFactory
from django.test.testcases import TestCase


class IntegrationCameraMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id
        return super().setUp()

    @patch('alarm.notifications.object_detected')
    @patch('automation.tasks.on_motion_detected')
    def test_integration_camera_motion(self, on_motion_detected, object_detected):
        integration_camera_motion(self.device)

        d = {'device_id': self.device_id}
        on_motion_detected.apply_async.assert_called_once_with(kwargs=d)

        object_detected.assert_called_once_with(self.device)

    @patch('automation.tasks.on_motion_left')
    @patch('alarm.notifications.object_no_more_detected')
    def test_integration_camera_no_more_motion(self, object_no_more_detected, on_motion_left):
        integration_camera_no_more_motion(self.device)

        d = {'device_id': self.device_id}
        on_motion_left.apply_async.assert_called_once_with(kwargs=d)

        object_no_more_detected.assert_called_once_with(self.device)

