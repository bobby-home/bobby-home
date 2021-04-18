import uuid
from devices.factories import DeviceFactory
from alarm.use_cases.data import InMotionVideoData
from unittest.mock import patch, MagicMock, call

from django.test import TestCase
from alarm.use_cases.camera_video import CameraVideo


class CameraVideoTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id

        self.device2 = DeviceFactory()
        self.device2_id = self.device2.device_id

        self.video_folder = '/usr/random'

        self.video_split_number = 1
        self.event_ref = str(uuid.uuid4())
        
        self.video_ref = f'{self.event_ref}-{self.video_split_number}'
        self.video_ref_fist_video = f'{self.event_ref}-0'
        self.camera_video = CameraVideo(self.video_folder, self.device_id)

        self.data = InMotionVideoData(
                device_id=self.device_id,
                video_ref=self.video_ref,
                event_ref=self.event_ref,
                video_split_number=self.video_split_number
        )
        
        self.data_first_video = InMotionVideoData(
            device_id=self.device_id,
            video_ref=self.video_ref_fist_video,
            event_ref=self.event_ref,
            video_split_number=0
        )

        self.data_remote_device = InMotionVideoData(
            device_id=self.device2_id,
            video_ref=self.video_ref,
            event_ref=self.event_ref,
            video_split_number=self.video_split_number
        )

        self.data_remote_first_video = InMotionVideoData(
            device_id=self.device2_id,
            video_ref=self.video_ref_fist_video,
            event_ref=self.event_ref,
            video_split_number=0
        )
    
    def _setup_video_ref_var(self, data: InMotionVideoData):
        self.output_video = f'{self.video_folder}/{data.video_ref}.mp4'
        self.raw_video = f'{self.video_folder}/{data.video_ref}.h264'

        self.before_raw_video = f'{self.video_folder}/{data.video_ref}-before.h264'
        self.before_raw_video_merged = f'{self.video_folder}/{data.video_ref}-merged.h264'

    @patch('alarm.utils.video_processing.retrieve_video_remotely')
    @patch('alarm.utils.video_processing.merge_videos')
    @patch('notification.tasks.send_video')
    @patch('alarm.utils.video_processing.h264_to_mp4')
    def test_camera_video_self_device(self, h264_to_mp4: MagicMock, send_video: MagicMock, merge_videos: MagicMock, retrieve_video_remotely: MagicMock):
        self.camera_video.camera_video(self.data)
        self._setup_video_ref_var(self.data)

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
        data = self.data_remote_device
        self.camera_video.camera_video(data)
        self._setup_video_ref_var(data)

        h264_to_mp4.assert_called_once_with(
            self.raw_video,
            self.output_video
        )

        send_video.assert_called_once_with(self.output_video)

        merge_videos.assert_not_called()

        retrieve_video_remotely.assert_called_once_with(
            f'{CameraVideo.REMOTE_VIDEO_FOLDER}{data.video_ref}.h264',
            self.raw_video,
            self.device2_id
        )


    @patch('alarm.utils.video_processing.retrieve_video_remotely')
    @patch('alarm.utils.video_processing.merge_videos')
    @patch('notification.tasks.send_video')
    @patch('alarm.utils.video_processing.h264_to_mp4')
    def test_camera_first_video_self_device(self, h264_to_mp4: MagicMock, send_video: MagicMock, merge_videos: MagicMock, retrieve_video_remotely: MagicMock):
        data = self.data_first_video
        self.camera_video.camera_video(data)
        self._setup_video_ref_var(data)

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
        data = self.data_remote_first_video
        self.camera_video.camera_video(data)
        self._setup_video_ref_var(data)

        retrieve_video_remotely.assert_has_calls([
            call(
                f'{CameraVideo.REMOTE_VIDEO_FOLDER}{data.video_ref}.h264',
                self.raw_video,
                self.device2_id),
            call(
                f'{CameraVideo.REMOTE_VIDEO_FOLDER}{data.video_ref}-before.h264',
                self.before_raw_video,
                self.device2_id)
        ])

        merge_videos.assert_called_once_with([self.before_raw_video, self.raw_video], self.before_raw_video_merged)

        h264_to_mp4.assert_called_once_with(
            self.before_raw_video_merged,
            self.output_video
        )

        send_video.assert_called_once_with(self.output_video)
