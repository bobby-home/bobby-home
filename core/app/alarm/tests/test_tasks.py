from alarm.use_cases.data import InMotionCameraData
from unittest.mock import Mock, patch
from django.test.testcases import TestCase
from alarm.tasks import camera_motion_detected

class CameraMotionDetectedTaskTestCase(TestCase):
    def _get_payload(self, status):
        payload = {
            'device_id': 'some_device_id',
            'event_ref': 'some_event_ref',
            'status': status,
            'detections': []
        }
        d = InMotionCameraData(**payload)
        return (payload, d)

    @patch('alarm.use_cases.camera_motion.camera_motion_factory')
    def test_motion(self, mock):
        motion_mock = Mock()
        mock.return_value = motion_mock
        dict_payload, data = self._get_payload(True)
        camera_motion_detected(dict_payload)

        mock.assert_called_once_with()
        motion_mock.motion_detected.assert_called_once_with(data)
        motion_mock.motion_detect_ended.assert_not_called()

    @patch('alarm.use_cases.camera_motion.camera_motion_factory')
    def test_no_motion(self, mock):
        motion_mock = Mock()
        mock.return_value = motion_mock
        dict_payload, data = self._get_payload(False)
        camera_motion_detected(dict_payload)

        mock.assert_called_once_with()
        motion_mock.motion_detect_ended.assert_called_once_with(data)
        motion_mock.motion_detected.assert_not_called()

    @patch('alarm.use_cases.camera_motion.camera_motion_factory')
    def test_wrong_status(self, mock):
        """
        It only accepts boolean values, otherwise it won't do anything.
        This could be dangerous tho... Ensured in front it's python boolean.
        """
        motion_mock = Mock()
        mock.return_value = motion_mock
        dict_payload, data = self._get_payload('false')
        camera_motion_detected(dict_payload)

        mock.assert_called_once_with()
        motion_mock.motion_detect_ended.assert_not_called()
        motion_mock.motion_detected.assert_not_called()


