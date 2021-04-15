from typing import Sequence
import uuid
import unittest
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone

from alarm.mqtt.mqtt import CameraMotionPictureTopic, CameraMotionVideoTopic, CameraTopic, on_motion_picture, split_camera_topic, topic_regex
from devices.factories import DeviceFactory
from utils.mqtt import MqttMessage


class ExtractTopicData(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_motion_camera(self):
        topic = 'motion/camera/something/ref'
        print(split_camera_topic(topic))
        data = topic_regex(topic, CameraMotionVideoTopic)
        
        print('data:', data)
        
        
    
    def test_motion_picture(self):
        topic = 'motion/picture/1/2/3'
        print(split_camera_topic(topic, True))
    
    def test_motion_video(self):
        topic = 'motion/video/1/2'

        print(split_camera_topic(topic, True))

class OnMotionPictureTestCase(TestCase):
    def setUp(self, ) -> None:
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

            camera_motion_picture.apply_async.assert_called_once_with(kwargs=kwargs)

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

            camera_motion_picture.apply_async.assert_called_once_with(kwargs=kwargs)
