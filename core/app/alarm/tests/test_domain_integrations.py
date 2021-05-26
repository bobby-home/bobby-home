from alarm.domain_integrations import on_motion
from unittest.mock import Mock, patch
from django.test import TestCase

class YoloTestCase(TestCase):
    @patch('automation.tasks.on_motion_detected')
    @patch('automation.tasks.on_motion_left')
    def test_call_on_motion(self, on_motion_left_mock, on_motion_detected_mock):
        on_motion(True)

        on_motion_detected_mock.apply_async.assert_called_once_with()
        on_motion_left_mock.apply_async.assert_not_called()

    @patch('automation.tasks.on_motion_detected')
    @patch('automation.tasks.on_motion_left')
    def test_call_left_motion(self, on_motion_left_mock, on_motion_detected_mock):
        on_motion(False)

        on_motion_left_mock.apply_async.assert_called_once_with()
        on_motion_detected_mock.apply_async.assert_not_called()
