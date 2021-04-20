from alarm.use_cases.data import InMotionVideoData
from devices.factories import DeviceFactory
import uuid

from django.test import TransactionTestCase

from alarm.business.in_motion import save_camera_video
from camera.models import CameraMotionVideo


class SaveCameraVideoTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id
        self.event_ref = str(uuid.uuid4())

        self.video_ref_first_video = f'{self.event_ref}-0'
        self.video_ref_video = f'{self.event_ref}-1'

        self.data_first_video = InMotionVideoData(
            device_id=self.device_id,
            video_ref=self.video_ref_first_video,
            event_ref=self.event_ref,
            video_split_number=0
        )

        self.data = InMotionVideoData(
            device_id=self.device_id,
            video_ref=self.video_ref_video,
            event_ref=self.event_ref,
            video_split_number=1
        )


    def test_save_camera_video(self):
        save_camera_video(self.data_first_video)

        video = CameraMotionVideo.objects.get(device=self.device, event_ref=self.event_ref)
        
        self.assertEqual(video.number_records, 0)
        self.assertEqual(str(video.event_ref), self.event_ref)
        self.assertFalse(video.is_merged)

    def test_save_camera_video_uniqueness(self):
        save_camera_video(self.data_first_video)
        save_camera_video(self.data)

        videos = CameraMotionVideo.objects.filter(device=self.device, event_ref=self.event_ref)
        
        self.assertEqual(1, len(videos))
        video = videos[0]

        self.assertEqual(video.number_records, 1)
        self.assertEqual(str(video.event_ref), self.event_ref)
        self.assertFalse(video.is_merged)

    def test_save_camera_video_nb_records(self):
        event_ref = str(uuid.uuid4())
        CameraMotionVideo.objects.create(
            device=self.device,
            event_ref=event_ref,
            number_records=4
        )

        save_camera_video(self.data)
        videos = CameraMotionVideo.objects.filter(device=self.device, event_ref=event_ref)
        
        self.assertEqual(1, len(videos))
        video = videos[0]

        self.assertEqual(video.number_records, 4)
