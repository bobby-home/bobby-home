from datetime import timedelta
from django.utils import timezone
from alarm.use_cases.alarm_camera_video_manager import _split_messages
from devices.factories import DeviceFactory
from camera.factories import CameraMotionDetectedFactory, CameraMotionVideoFactory
from django.test.testcases import TestCase


class AlarmCameraVideoManager(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()

        self.motions = (
            CameraMotionDetectedFactory(device=self.device),
            CameraMotionDetectedFactory(device=self.device),
        )

        old_time = timezone.now() - timedelta(minutes=10)
        print(f'test time last_record={old_time}')

        self.videos = (
            CameraMotionVideoFactory(device=self.device, event_ref=self.motions[0].event_ref, last_record=old_time),
            CameraMotionVideoFactory(device=self.device, event_ref=self.motions[1].event_ref, number_records=1, last_record=old_time),
        )
        print('videos:', self.videos)
        return super().setUp()

    def test_messages(self):
        messages = _split_messages()
        self.assertEqual(2, len(messages))
        for i, message in enumerate(messages):
            video = self.videos[i]
            self.assertEqual(message['topic'], f'camera/recording/{self.device.device_id}/split/{video.event_ref}-{video.number_records+1}')

        print(f'messages={messages}')
