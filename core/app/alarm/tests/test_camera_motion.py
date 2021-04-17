import uuid
from alarm.mqtt.mqtt_data import InMotionCameraData
from unittest.mock import Mock, patch
from django.test import TestCase

from alarm.communication.camera_motion import camera_motion_detected
from alarm.factories import AlarmStatusFactory
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetected 
from devices.factories import DeviceFactory


class CameraMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id
        self.alarm_status = AlarmStatusFactory(device=self.device, running=False)
        self.event_ref = str(uuid.uuid4())

        self.notify_alarm_status_mock = Mock()

    @patch('alarm.communication.camera_motion.play_sound')
    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.communication.out_alarm.notify_alarm_status_factory')
    def test_camera_motion_detected(self, notify_alarm_status_mock, object_no_more_detected_mock, alarm_notifications_mock, play_sound_mock):
        in_data = InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=True, seen_in={})
        camera_motion_detected(in_data)
        
        play_sound_mock.assert_called_once_with(self.device.device_id, True)
        alarm_notifications_mock.assert_called_once_with(self.device)
        object_no_more_detected_mock.assert_not_called()

        motion = CameraMotionDetected.objects.filter(event_ref=self.event_ref, device=self.device)
        self.assertTrue(len(motion), 1)

        notify_alarm_status_mock.assert_not_called()

    @patch('alarm.communication.camera_motion.play_sound')
    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.communication.out_alarm.notify_alarm_status_factory')
    def test_camera_motion_no_more_motion(self, _notify_alarm_status_mock, object_no_more_detected_mock, object_detected_mock, play_sound_mock):
        in_data = InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=True, seen_in={})
        camera_motion_detected(in_data)
        object_detected_mock.reset_mock()
        play_sound_mock.reset_mock()

        in_data = InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=False, seen_in={})
        camera_motion_detected(in_data)
        
        play_sound_mock.assert_called_once_with(self.device.device_id, False)
        object_no_more_detected_mock.assert_called_once_with(self.device)

        motion = CameraMotionDetected.objects.filter(event_ref=str(self.event_ref), device=self.device)
        self.assertTrue(len(motion), 1)

    @patch('alarm.communication.camera_motion.play_sound')
    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.communication.out_alarm.notify_alarm_status_factory')
    def test_camera_motion_no_more_motion_turn_off(self, notify_alarm_status_mock, object_no_more_detected_mock, object_detected_mock, play_sound_mock):
        """
        When no more motion is being detected on a camera and its database status is False, it should turn off the camera.
        """
        AlarmStatus.objects.all().delete()
        self.alarm_status = AlarmStatusFactory(device=self.device, running=False)

        mock = Mock()
        notify_alarm_status_mock.return_value = mock

        in_data = InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=True, seen_in={})
        camera_motion_detected(in_data)
        object_detected_mock.reset_mock()

        in_data = InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=False, seen_in={})
        camera_motion_detected(in_data)

        object_no_more_detected_mock.assert_called_once_with(self.device)
        object_detected_mock.assert_not_called()

        notify_alarm_status_mock.assert_called_once_with()
        mock.publish_status_changed.assert_called_once_with(self.device.pk, self.alarm_status)


    @patch('alarm.communication.camera_motion.play_sound')
    @patch('alarm.notifications.object_detected')
    @patch('alarm.notifications.object_no_more_detected')
    @patch('alarm.communication.out_alarm.notify_alarm_status_factory')
    def test_camera_motion_no_more_motion_dont_turn_off(self, notify_alarm_status_mock, object_no_more_detected_mock, object_detected_mock, play_sound_mock):
        AlarmStatus.objects.all().delete()
        self.alarm_status = AlarmStatusFactory(device=self.device, running=True)

        in_data = InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=True, seen_in={})
        camera_motion_detected(in_data)
        in_data = InMotionCameraData(device_id=self.device_id, event_ref=self.event_ref, status=False, seen_in={})
        camera_motion_detected(in_data)


        notify_alarm_status_mock.publish_status_changed.assert_not_called()
