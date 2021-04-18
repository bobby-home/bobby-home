from alarm.use_cases.data import InMotionCameraData, InMotionPictureData, InMotionVideoData
import dataclasses
import uuid
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone

from alarm.mqtt.mqtt_controller import CameraMotionPictureTopic, CameraMotionTopic, CameraMotionVideoTopic, on_motion_camera, on_motion_picture, on_motion_video, topic_regex
from devices.factories import DeviceFactory
from utils.mqtt import MqttMessage


class ExtractTopicData(TestCase):
    def setUp(self) -> None:
        self.event_ref = str(uuid.uuid4())
        self.device = DeviceFactory()
        self.device_id = self.device.device_id

    def test_motion_camera(self):
        topic = f'motion/camera/{self.device_id}'
        data = topic_regex(topic, CameraMotionTopic)
        expected = CameraMotionTopic(
            type='motion',
            service='camera',
            device_id=self.device_id,
        )
        self.assertEqual(dataclasses.asdict(data), dataclasses.asdict(expected)) 
    
    def test_motion_picture(self):
        topic = f'motion/picture/{self.device_id}/{self.event_ref}/0'
        topic_true_status = f'motion/picture/{self.device_id}/{self.event_ref}/1'
        data = topic_regex(topic, CameraMotionPictureTopic)

        expected = CameraMotionPictureTopic(
            type='motion',
            service='picture',
            device_id=self.device_id,
            event_ref=self.event_ref,
            status='0',
        )

        self.assertFalse(expected.bool_status)
        self.assertEqual(dataclasses.asdict(data), dataclasses.asdict(expected))

        data = topic_regex(topic_true_status, CameraMotionPictureTopic)
        expected = CameraMotionPictureTopic(
            type='motion',
            service='picture',
            device_id=self.device_id,
            event_ref=self.event_ref,
            status='1',
        )

        self.assertTrue(expected.bool_status)
        self.assertEqual(dataclasses.asdict(data), dataclasses.asdict(expected))
    
    
    def test_motion_video(self):
        video_split = 2
        topic = f'motion/video/{self.device_id}/{self.event_ref}-{video_split}'
        data = topic_regex(topic, CameraMotionVideoTopic)

        expected = CameraMotionVideoTopic(
            type='motion',
            service='video',
            device_id=self.device_id,
            event_ref=f'{self.event_ref}',
            video_split_number=video_split
        )
        self.assertEqual(dataclasses.asdict(data), dataclasses.asdict(expected))


class OnMotionPictureTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.event_ref = str(uuid.uuid4())
        self.service_name = 'some_service_name'
        self.device_id = '1234567'
        self.false_topic = f'motion/picture/{self.device.device_id}/{self.event_ref}/0'
        self.true_topic = f'motion/picture/{self.device.device_id}/{self.event_ref}/1'
        self.retain = False
        self.qos = 1
        self.payload = b''

        self.timestamp = timezone.now()

    def test_on_motion_picture_no_motion(self):
        message = MqttMessage(
            self.false_topic,
            self.payload,
            self.qos,
            self.retain,
            self.false_topic,
            self.timestamp,
        )

        with patch('alarm.tasks.camera_motion_picture') as camera_motion_picture:
            on_motion_picture(message)

            kwargs = {
                'device_id': self.device.device_id,
                'picture_path': f'/var/lib/house/media/{self.event_ref}.jpg',
                'event_ref': self.event_ref,
                'status': False,
            }

            in_data = InMotionPictureData(**kwargs)

            camera_motion_picture.apply_async.assert_called_once_with(args=[dataclasses.asdict(in_data)])

    def test_on_motion_picture_motion(self):
        message = MqttMessage(
            self.true_topic,
            self.payload,
            self.qos,
            self.retain,
            self.true_topic,
            self.timestamp,
        )

        with patch('alarm.tasks.camera_motion_picture') as camera_motion_picture:
            on_motion_picture(message)

            kwargs = {
                'device_id': self.device.device_id,
                'picture_path': f'/var/lib/house/media/{self.event_ref}.jpg',
                'event_ref': self.event_ref,
                'status': True,
            }
            
            in_data = InMotionPictureData(**kwargs)

            camera_motion_picture.apply_async.assert_called_once_with(args=[dataclasses.asdict(in_data)])


class OnMotionVideoTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.device = DeviceFactory()
        self.device_id = self.device.device_id

        self.video_number_split = '2'
        self.event_ref = str(uuid.uuid4())
        self.video_ref = f'{self.event_ref}-{self.video_number_split}'
        
        self.topic = f'motion/video/{self.device_id}/{self.video_ref}'
        self.qos = 1
        self.retain = True
        self.payload = b''
        self.timestamp = timezone.now()

    def test_on_motion_video(self):
        message = MqttMessage(
            self.topic,
            self.payload,
            self.qos,
            self.retain,
            None,
            self.timestamp,
        )

        with patch('alarm.tasks.camera_motion_video') as camera_motion_video:
            on_motion_video(message)

            in_data = InMotionVideoData(self.device_id, self.video_ref, self.event_ref, int(self.video_number_split))

            camera_motion_video.apply_async.assert_called_once_with(args=[dataclasses.asdict(in_data)], countdown=3)


class OnMotionTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.event_ref = str(uuid.uuid4())
        self.device = DeviceFactory()
        self.device_id = self.device.device_id
        self.status = False
        self.seen_in = {'full': True}

        self.topic = f'motion/picture/{self.device.device_id}/{self.event_ref}/1'
        self.retain = False
        self.qos = 1
        self.payload = {'event_ref': self.event_ref, 'status': self.status, 'seen_in': self.seen_in}
        self.timestamp = timezone.now()

    def test_camera_motion(self) -> None:
        message = MqttMessage(
            self.topic,
            self.payload,
            self.qos,
            self.retain,
            None,
            self.timestamp,
        )

        with patch('alarm.tasks.camera_motion_detected') as camera_motion_detected:
            on_motion_camera(message)
            
            expected = InMotionCameraData(
                device_id=self.device_id, event_ref=self.event_ref, status=self.status, seen_in=self.seen_in
            )
            camera_motion_detected.apply_async.assert_called_once_with(args=[dataclasses.asdict(expected)])

