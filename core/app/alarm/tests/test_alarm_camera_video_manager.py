from unittest.mock import Mock
from datetime import timedelta
from utils.mqtt import MQTTMessage, MQTTOneShoot
from django.utils import timezone
from alarm.use_cases.alarm_camera_video_manager import AlarmCameraVideoManager, _split_messages
from devices.factories import DeviceFactory
from camera.factories import CameraMotionDetectedFactory, CameraMotionVideoFactory
from django.test.testcases import TestCase


class AlarmCameraVideoManagerTestCase(TestCase):
    def setUp(self) -> None:
        self.mqtt_mock = Mock(spec_set=MQTTOneShoot)
        self.manager = AlarmCameraVideoManager(self.mqtt_mock)
        self.device = DeviceFactory()

        self.motions = (
            CameraMotionDetectedFactory(device=self.device),
            CameraMotionDetectedFactory(device=self.device),
        )


        old_time = timezone.now() - timedelta(minutes=10)

        self.videos = (
            CameraMotionVideoFactory(device=self.device, event_ref=self.motions[0].event_ref, last_record=old_time),
            CameraMotionVideoFactory(device=self.device, event_ref=self.motions[1].event_ref, number_records=1, last_record=old_time),
        )
        return super().setUp()

    def test_messages(self):
        messages = _split_messages()
        self.assertEqual(2, len(messages))
        for i, message in enumerate(messages):
            video = self.videos[i]
            self.assertEqual(message.topic, f'camera/recording/{self.device.device_id}/split/{video.event_ref}-{video.number_records+1}')

    def test_split_recording(self):
        ref = 'job_uuid'
        self.manager.split_recordings(ref)
        messages = _split_messages()
        self.mqtt_mock.multiple.assert_called_once_with(messages, f'split_recordings-{ref}')

    def test_start_recording(self):
        motion = CameraMotionDetectedFactory(device=self.device)

        event_ref = f'{motion.event_ref}-0'
        self.manager.start_recording(self.device.device_id, motion.event_ref)
        self.mqtt_mock.single.assert_called_once_with(MQTTMessage(topic=f'camera/recording/{self.device.device_id}/start/{event_ref}'), f'start_recording-{motion.event_ref}')

    def test_stop_recording(self):
        motion = CameraMotionDetectedFactory(device=self.device)
        video = CameraMotionVideoFactory(device=self.device, event_ref=motion.event_ref, number_records=3)

        event_ref = f'{motion.event_ref}-{video.number_records}'
        self.manager.stop_recording(self.device.device_id, motion.event_ref)
        self.mqtt_mock.single.assert_called_once_with(MQTTMessage(topic=f'camera/recording/{self.device.device_id}/stop/{event_ref}'), f'stop_recording-{motion.event_ref}')
