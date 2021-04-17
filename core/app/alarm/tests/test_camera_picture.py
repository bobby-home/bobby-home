import uuid
from django.test import TestCase
from alarm.mqtt.mqtt_data import InMotionPictureData
from unittest.mock import Mock, patch
from alarm.factories import AlarmStatusFactory
from camera.models import CameraMotionDetectedPicture
from devices.factories import DeviceFactory
from alarm.communication.camera_picture import camera_motion_picture


class CameraMotionPictureTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id
        self.alarm_status = AlarmStatusFactory(device=self.device, running=False)
        self.event_ref = str(uuid.uuid4())

        self.create_and_send_notification = Mock()
        self.play_sound = Mock()
        self.send_picture = Mock()

        self.notify_alarm_status_mock = Mock()
        self.notify_alarm_status_factory = lambda : self.notify_alarm_status_mock


    def test_camera_motion_picture(self):
        fake_picture_path = '/some/path.png'
        
        with patch('notification.tasks.send_picture') as send_picture_mock:
            in_data1 =InMotionPictureData(
                device_id=self.device_id,
                picture_path=fake_picture_path,
                event_ref=self.event_ref,
                status=True
            )

            camera_motion_picture(in_data1)

            motion = CameraMotionDetectedPicture.objects.filter(event_ref=self.event_ref, device=self.device)
            self.assertTrue(len(motion), 1)
            motion = motion[0]

            self.assertEqual(motion.motion_started_picture.name, 'path.png')
            self.assertEqual(motion.motion_ended_picture.name, '')

            kwargs = {
                'picture_path': fake_picture_path
            }

            send_picture_mock.apply_async.assert_called_once_with(kwargs=kwargs)

    def test_camera_motion_picture_no_more_motion(self):
        fake_picture_path = '/some/path.png'
        fake_picture_path2 = '/some/path2.png'

        in_data1 =InMotionPictureData(
            device_id=self.device_id,
            picture_path=fake_picture_path,
            event_ref=self.event_ref,
            status=True
        )

        in_data2 =InMotionPictureData(
            device_id=self.device_id,
            picture_path=fake_picture_path2,
            event_ref=self.event_ref,
            status=False
        )

        with patch('notification.tasks.send_picture') as _send_picture:
            camera_motion_picture(in_data1)
            camera_motion_picture(in_data2)

            motion = CameraMotionDetectedPicture.objects.filter(event_ref=str(self.event_ref), device=self.device)
            self.assertTrue(len(motion), 1)
            motion = motion[0]

            self.assertEqual(motion.motion_started_picture.name, 'path.png')
            self.assertEqual(motion.motion_ended_picture.name, 'path2.png')


