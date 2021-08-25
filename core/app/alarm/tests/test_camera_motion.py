import uuid
from alarm.use_cases.data import InMotionCameraData
from unittest.mock import Mock, patch
from django.test import TestCase

from alarm.use_cases.camera_motion import camera_motion_detected
from alarm.factories import AlarmStatusFactory
from alarm.models import AlarmStatus
from devices.factories import DeviceFactory


class CameraMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id
        self.alarm_status = AlarmStatusFactory(device=self.device, running=True)
        self.event_ref = str(uuid.uuid4())

        self.notify_alarm_status_mock = Mock()

    def _get_in_motion_camera_data(self, status: bool) -> InMotionCameraData:
        return InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=status, detections=[])

    def _assert_save_motion(self, save_motion_mock, status: bool) -> None:
        save_motion_mock.assert_called_once_with(self.device, [], self.event_ref, status)

    @patch('alarm.business.in_motion.save_motion')
    @patch('alarm.use_cases.camera_motion.integration_camera_motion')
    @patch('alarm.use_cases.camera_motion.integration_alarm_status_changed')
    @patch('alarm.use_cases.camera_motion.integration_camera_no_more_motion')
    def test_camera_motion_detected(self, integration_camera_no_more_motion, integration_alarm_status_changed, integration_camera_motion, save_motion_mock):
        in_data = self._get_in_motion_camera_data(status=True)
        camera_motion_detected(in_data)
        self._assert_save_motion(save_motion_mock, status=True)

        integration_camera_motion.assert_called_once_with(self.device)
        integration_camera_no_more_motion.assert_not_called()
        integration_alarm_status_changed.assert_not_called()

    @patch('alarm.business.in_motion.save_motion')
    @patch('alarm.use_cases.camera_motion.integration_camera_motion')
    @patch('alarm.use_cases.camera_motion.integration_alarm_status_changed')
    @patch('alarm.use_cases.camera_motion.integration_camera_no_more_motion')
    def test_camera_motion_no_more_motion(self, integration_camera_no_more_motion, integration_alarm_status_changed, integration_camera_motion, save_motion_mock):
        in_data = self._get_in_motion_camera_data(status=True)
        camera_motion_detected(in_data)
        self._assert_save_motion(save_motion_mock, status=True)

        integration_alarm_status_changed.reset_mock()
        integration_camera_no_more_motion.reset_mock()
        integration_camera_motion.reset_mock()
        save_motion_mock.reset_mock()

        in_data = self._get_in_motion_camera_data(status=False)
        camera_motion_detected(in_data)

        self._assert_save_motion(save_motion_mock, status=False)

        integration_camera_no_more_motion.assert_called_once_with(self.device)
        integration_alarm_status_changed.assert_not_called()
        integration_camera_motion.assert_not_called()

    @patch('alarm.business.in_motion.save_motion')
    @patch('alarm.use_cases.camera_motion.integration_camera_motion')
    @patch('alarm.use_cases.camera_motion.integration_alarm_status_changed')
    @patch('alarm.use_cases.camera_motion.integration_camera_no_more_motion')
    def test_camera_motion_no_more_motion_call_alarm_status_integration(self, integration_camera_no_more_motion, integration_alarm_status_changed, integration_camera_motion, save_motion_mock):
        AlarmStatus.objects.all().delete()
        self.alarm_status = AlarmStatusFactory(device=self.device, running=False)

        in_data = self._get_in_motion_camera_data(status=True)
        camera_motion_detected(in_data)
        self._assert_save_motion(save_motion_mock, status=True)

        integration_alarm_status_changed.reset_mock()
        integration_camera_no_more_motion.reset_mock()
        integration_camera_motion.reset_mock()
        save_motion_mock.reset_mock()

        in_data = self._get_in_motion_camera_data(status=False)
        camera_motion_detected(in_data)

        self._assert_save_motion(save_motion_mock, status=False)

        integration_camera_no_more_motion.assert_called_once_with(self.device)
        integration_alarm_status_changed.assert_called_once_with(self.alarm_status)
        integration_camera_motion.assert_not_called()
