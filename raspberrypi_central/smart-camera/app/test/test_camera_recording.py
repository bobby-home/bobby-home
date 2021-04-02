import json
from io import BytesIO
from unittest import TestCase, skip
from unittest.mock import Mock, patch, call

from camera.camera_object_detection import CameraObjectDetection
from camera.camera_recording import CameraRecording
from datetime import datetime, timedelta


class TestCameraRecording(TestCase):
    def setUp(self) -> None:
        self.device_id = 'some_uuid'
        self.event_ref = 'some_event_ref'

        self.camera_recorder_mock = Mock()
        self.camera_recording = CameraRecording(self.device_id, self.camera_recorder_mock)

    def test_start_record_video(self):
        self.camera_recording.start_recording(self.event_ref)
        self.camera_recording.start_recording(self.event_ref)
        self.camera_recorder_mock.start_recording.assert_called_once_with(f'{self.event_ref}-0')

    def test_split_record_video(self):
        self.camera_recording.start_recording(self.event_ref)
        self.camera_recording.split_recording(self.event_ref)

        self.camera_recorder_mock.split_recording.assert_not_called()

        with patch('utils.time.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=CameraRecording.SECONDS_FIRST_MOTION_VIDEO)
            video_ref = self.camera_recording.split_recording(self.event_ref)
            self.camera_recording.split_recording(self.event_ref)

            self.assertEqual(video_ref, f'{self.event_ref}-0')
            self.camera_recorder_mock.split_recording.assert_called_once_with(f'{self.event_ref}-1')

        self.camera_recorder_mock.reset_mock()

        with patch('utils.time.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=CameraRecording.SECONDS_MOTION_VIDEO)
            video_ref = self.camera_recording.split_recording(self.event_ref)
            self.assertEqual(video_ref, f'{self.event_ref}-1')
            self.camera_recorder_mock.split_recording.assert_called_once_with(f'{self.event_ref}-2')

    def test_stop_record_video(self):
        self.camera_recording.start_recording(self.event_ref)

        video_ref = self.camera_recording.stop_recording(self.event_ref)
        self.camera_recorder_mock.stop_recording.assert_called_once_with()

        self.assertEqual(video_ref, f'{self.event_ref}-0')

        self.camera_recorder_mock.reset_mock()
        self.camera_recording.start_recording(self.event_ref)

        with patch('utils.time.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=CameraRecording.SECONDS_MOTION_VIDEO)
            video_ref = self.camera_recording.split_recording(self.event_ref)

        video_ref = self.camera_recording.stop_recording(self.event_ref)
        self.assertEqual(video_ref, f'{self.event_ref}-1')
