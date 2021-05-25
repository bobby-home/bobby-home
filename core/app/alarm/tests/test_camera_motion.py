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
        self.alarm_status = AlarmStatusFactory(device=self.device, running=False)
        self.event_ref = str(uuid.uuid4())

        self.notify_alarm_status_mock = Mock()

    def _get_in_motion_camera_data(self, status: bool) -> InMotionCameraData:
        return InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=status, detections=[])

    def _assert_save_motion(self, save_motion_mock, status: bool) -> None:
        save_motion_mock.assert_called_once_with(self.device, [], self.event_ref, status)

    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.use_cases.out_alarm.notify_alarm_status_factory')
    @patch('alarm.business.in_motion.save_motion')
    @patch('automation.tasks.on_motion_detected')
    @patch('automation.tasks.on_motion_left')
    def test_camera_motion_detected(self, on_motion_left, on_motion_detected, save_motion_mock, notify_alarm_status_mock, object_no_more_detected_mock, alarm_notifications_mock):
        in_data = self._get_in_motion_camera_data(status=True)
        camera_motion_detected(in_data)
        self._assert_save_motion(save_motion_mock, status=True)

        d = {'device_id': self.device_id}
        on_motion_detected.apply_async.assert_called_once_with(kwargs=d)
        on_motion_left.apply_async.assert_not_called()

        alarm_notifications_mock.assert_called_once_with(self.device)
        object_no_more_detected_mock.assert_not_called()

        notify_alarm_status_mock.assert_not_called()

    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.use_cases.out_alarm.notify_alarm_status_factory')
    @patch('alarm.business.in_motion.save_motion')
    @patch('automation.tasks.on_motion_detected')
    @patch('automation.tasks.on_motion_left')
    def test_camera_motion_no_more_motion(self, on_motion_left, on_motion_detected, save_motion_mock, notify_alarm_status_mock, object_no_more_detected_mock, object_detected_mock):
        in_data = self._get_in_motion_camera_data(status=True)
        camera_motion_detected(in_data)
        self._assert_save_motion(save_motion_mock, status=True)
        object_detected_mock.reset_mock()
        save_motion_mock.reset_mock()
        on_motion_left.reset_mock()
        on_motion_detected.reset_mock()

        in_data = self._get_in_motion_camera_data(status=False)
        camera_motion_detected(in_data)

        self._assert_save_motion(save_motion_mock, status=False)
        object_no_more_detected_mock.assert_called_once_with(self.device)

        d = {'device_id': self.device_id}
        on_motion_left.apply_async.assert_called_once_with(kwargs=d)
        on_motion_detected.apply_async.assert_not_called()

    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.use_cases.out_alarm.notify_alarm_status_factory')
    def test_camera_motion_no_more_motion_turn_off(self, notify_alarm_status_mock, object_no_more_detected_mock, object_detected_mock):
        """
        When no more motion is being detected on a camera and its database status is False, it should turn off the camera.
        """
        AlarmStatus.objects.all().delete()
        self.alarm_status = AlarmStatusFactory(device=self.device, running=False)

        mock = Mock()
        notify_alarm_status_mock.return_value = mock

        in_data = self._get_in_motion_camera_data(status=True)
        camera_motion_detected(in_data)
        object_detected_mock.reset_mock()

        in_data = self._get_in_motion_camera_data(status=False)
        camera_motion_detected(in_data)

        object_no_more_detected_mock.assert_called_once_with(self.device)
        object_detected_mock.assert_not_called()

        notify_alarm_status_mock.assert_called_once_with()
        mock.publish_status_changed.assert_called_once_with(self.device.pk, self.alarm_status)

    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.use_cases.out_alarm.notify_alarm_status_factory')
    def test_camera_motion_no_more_motion_dont_turn_off(self, notify_alarm_status_mock, object_no_more_detected_mock, object_detected_mock):
        AlarmStatus.objects.all().delete()

        self.alarm_status = AlarmStatusFactory(device=self.device, running=True)

        in_data = self._get_in_motion_camera_data(status=True)
        camera_motion_detected(in_data)

        in_data = self._get_in_motion_camera_data(status=False)
        camera_motion_detected(in_data)

        notify_alarm_status_mock.publish_status_changed.assert_not_called()
