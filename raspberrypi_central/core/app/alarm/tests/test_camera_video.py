from unittest.mock import patch, MagicMock, call

from django.test import TestCase
from alarm.communication.camera_video import CameraVideo


class CameraVideoTestCase(TestCase):
    def setUp(self) -> None:
        self.video_folder = '/usr/random'
        self.device_id = 'some_device_id'
        self.another_device_id = 'another_device_id'
        self.video_ref = '1be409e1-7625-490a-9a8a-428ba4b8e88c-1'
        self.camera_video = CameraVideo(self.video_folder, self.device_id)
        self._setup_video_ref_var()

    def _setup_video_ref_var(self):
        self.output_video = f'{self.video_folder}/{self.video_ref}.mp4'
        self.raw_video = f'{self.video_folder}/{self.video_ref}.h264'

        self.before_raw_video = f'{self.video_folder}/{self.video_ref}-before.h264'
        self.before_raw_video_merged = f'{self.video_folder}/{self.video_ref}-merged.h264'

    @patch('alarm.utils.video_processing.retrieve_video_remotely')
    @patch('alarm.utils.video_processing.merge_videos')
    @patch('notification.tasks.send_video')
    @patch('alarm.utils.video_processing.h264_to_mp4')
    def test_camera_video_self_device(self, h264_to_mp4: MagicMock, send_video: MagicMock, merge_videos: MagicMock, retrieve_video_remotely: MagicMock):
        self.camera_video.camera_video(self.device_id, self.video_ref)

        h264_to_mp4.assert_called_once_with(
            self.raw_video,
            self.output_video
        )

        send_video.assert_called_once_with(self.output_video)

        merge_videos.assert_not_called()
        retrieve_video_remotely.assert_not_called()

    @patch('alarm.utils.video_processing.retrieve_video_remotely')
    @patch('alarm.utils.video_processing.merge_videos')
    @patch('notification.tasks.send_video')
    @patch('alarm.utils.video_processing.h264_to_mp4')
    def test_camera_video_remote(self, h264_to_mp4: MagicMock, send_video: MagicMock, merge_videos: MagicMock, retrieve_video_remotely: MagicMock):
        self.camera_video.camera_video(self.another_device_id, self.video_ref)

        h264_to_mp4.assert_called_once_with(
            self.raw_video,
            self.output_video
        )

        send_video.assert_called_once_with(self.output_video)

        merge_videos.assert_not_called()

        retrieve_video_remotely.assert_called_once_with(
            f'{CameraVideo.REMOTE_VIDEO_FOLDER}{self.video_ref}.h264',
            self.raw_video,
            self.another_device_id
        )


    @patch('alarm.utils.video_processing.retrieve_video_remotely')
    @patch('alarm.utils.video_processing.merge_videos')
    @patch('notification.tasks.send_video')
    @patch('alarm.utils.video_processing.h264_to_mp4')
    def test_camera_first_video_self_device(self, h264_to_mp4: MagicMock, send_video: MagicMock, merge_videos: MagicMock, retrieve_video_remotely: MagicMock):
        self.video_ref = '1be409e1-7625-490a-9a8a-428ba4b8e88c-0'
        self._setup_video_ref_var()

        self.camera_video.camera_video(self.device_id, self.video_ref)

        merge_videos.assert_called_once_with([self.before_raw_video, self.raw_video], self.before_raw_video_merged)

        h264_to_mp4.assert_called_once_with(
            self.before_raw_video_merged,
            self.output_video
        )

        send_video.assert_called_once_with(self.output_video)
        retrieve_video_remotely.assert_not_called()

    @patch('alarm.utils.video_processing.retrieve_video_remotely')
    @patch('alarm.utils.video_processing.merge_videos')
    @patch('notification.tasks.send_video')
    @patch('alarm.utils.video_processing.h264_to_mp4')
    def test_camera_first_video_remote(self, h264_to_mp4: MagicMock, send_video: MagicMock, merge_videos: MagicMock, retrieve_video_remotely: MagicMock):
        self.video_ref = '1be409e1-7625-490a-9a8a-428ba4b8e88c-0'
        self._setup_video_ref_var()

        self.camera_video.camera_video(self.another_device_id, self.video_ref)

        retrieve_video_remotely.assert_has_calls([
            call(
                f'{CameraVideo.REMOTE_VIDEO_FOLDER}{self.video_ref}.h264',
                self.raw_video,
                self.another_device_id),
            call(
                f'{CameraVideo.REMOTE_VIDEO_FOLDER}{self.video_ref}-before.h264',
                self.before_raw_video,
                self.another_device_id)
        ])

        merge_videos.assert_called_once_with([self.before_raw_video, self.raw_video], self.before_raw_video_merged)

        h264_to_mp4.assert_called_once_with(
            self.before_raw_video_merged,
            self.output_video
        )

        send_video.assert_called_once_with(self.output_video)
