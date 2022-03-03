import logging
from unittest.mock import Mock
from datetime import timedelta
from uuid import uuid4
from utils.mqtt import MQTTSendMessage, MQTTOneShoot
from django.utils import timezone
from alarm.use_cases.alarm_camera_video_manager import AlarmCameraVideoManager
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

    def test_split_recording_no_motion(self):
        uuid = str(uuid4())
        self.manager.split_recording(uuid)
        self.mqtt_mock.single.assert_not_called()

    def test_split_recording_first_video(self):
        """
        For the first video, we won't have any CameraMotionVideo in the database.
        It should ask to split the video with a split number set to 1.
        """
        motion = CameraMotionDetectedFactory(device=self.device)

        expected_topic = f'camera/recording/{motion.device.device_id}/split/{motion.event_ref}-1'
        expected_message = MQTTSendMessage(topic=expected_topic, payload=None, qos=1, retain=False)

        self.manager.split_recording(motion.event_ref)
        self.mqtt_mock.single.assert_called_once_with(expected_message, client_id=f'split_recording-{motion.event_ref}')

    def test_split_recording_motion(self):
        # the two are linked.
        motion = self.motions[0]
        video = self.videos[0]
        expected_topic = f'camera/recording/{motion.device.device_id}/split/{motion.event_ref}-{video.number_records+1}'
        expected_message = MQTTSendMessage(topic=expected_topic, payload=None, qos=1, retain=False)

        self.manager.split_recording(motion.event_ref)
        self.mqtt_mock.single.assert_called_once_with(expected_message, client_id=f'split_recording-{motion.event_ref}')

    def test_split_recording_motion_ended(self):
        motion = self.motions[0]
        motion.motion_ended_at = timezone.now()
        motion.save()

        self.manager.split_recording(motion.event_ref)
        self.mqtt_mock.single.assert_not_called()

    def test_start_recording(self):
        motion = CameraMotionDetectedFactory(device=self.device)

        event_ref = f'{motion.event_ref}-0'
        self.manager.start_recording(self.device.device_id, motion.event_ref)
        self.mqtt_mock.single.assert_called_once_with(MQTTSendMessage(topic=f'camera/recording/{self.device.device_id}/start/{event_ref}'), f'start_recording-{motion.event_ref}')

    def test_stop_recording(self):
        motion = CameraMotionDetectedFactory(device=self.device)
        video = CameraMotionVideoFactory(device=self.device, event_ref=motion.event_ref, number_records=3)

        event_ref = f'{motion.event_ref}-{video.number_records}'
        self.manager.stop_recording(self.device.device_id, motion.event_ref)
        self.mqtt_mock.single.assert_called_once_with(MQTTSendMessage(topic=f'camera/recording/{self.device.device_id}/end/{event_ref}'), f'stop_recording-{motion.event_ref}')
