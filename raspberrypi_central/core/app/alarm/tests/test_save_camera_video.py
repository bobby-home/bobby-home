import uuid

from django.test import TransactionTestCase

from alarm.business.in_motion import save_camera_video
from camera.models import CameraMotionVideo


class SaveCameraVideoTestCase(TransactionTestCase):
    def setUp(self) -> None:
        pass

    def test_save_camera_video(self):
        event_ref = str(uuid.uuid4())
        video_ref = f'{event_ref}-0'

        save_camera_video(video_ref)

        video = CameraMotionVideo.objects.get(event_ref=event_ref)
        self.assertEqual(video.number_records, 0)
        self.assertEqual(str(video.event_ref), event_ref)
        self.assertFalse(video.is_merged)

    def test_save_camera_video_uniqueness(self):
        event_ref = str(uuid.uuid4())

        video_ref = f'{event_ref}-0'
        save_camera_video(video_ref)

        video_ref = f'{event_ref}-1'
        save_camera_video(video_ref)

        video = CameraMotionVideo.objects.get(event_ref=event_ref)
        self.assertEqual(video.number_records, 1)
        self.assertEqual(str(video.event_ref), event_ref)
        self.assertFalse(video.is_merged)

    def test_save_camera_video_nb_records(self):
        event_ref = str(uuid.uuid4())
        CameraMotionVideo.objects.create(
            event_ref=event_ref,
            number_records=4
        )

        video_ref = f'{event_ref}-0'
        video = save_camera_video(video_ref)
        self.assertEqual(video.number_records, 4)
