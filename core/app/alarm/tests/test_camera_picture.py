import uuid
from django.db.utils import IntegrityError
from django.test import TestCase
from django.test.testcases import TransactionTestCase
from alarm.use_cases.data import InMotionPictureData
from unittest.mock import Mock, patch
from alarm.factories import AlarmStatusFactory
from camera.models import CameraMotionDetectedPicture
from devices.factories import DeviceFactory
from alarm.use_cases.camera_picture import camera_motion_picture


class CameraMotionPictureTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.device_id = self.device.device_id
        self.alarm_status = AlarmStatusFactory(device=self.device, running=False)
        self.event_ref = str(uuid.uuid4())

        self.create_and_send_notification = Mock()
        self.send_picture = Mock()

        self.notify_alarm_status_mock = Mock()
        self.notify_alarm_status_factory = lambda : self.notify_alarm_status_mock

        self.motion_picture_path = '/some/path.png'
        self.in_data_motion =InMotionPictureData(
            device_id=self.device_id,
            picture_path=self.motion_picture_path,
            event_ref=self.event_ref,
            status=True
        )

        self.no_motion_picture_path = '/some/path2.png'

        self.in_data_no_motion =InMotionPictureData(
            device_id=self.device_id,
            picture_path=self.no_motion_picture_path,
            event_ref=self.event_ref,
            status=False
        )

    def _get_motion(self):
        return CameraMotionDetectedPicture.objects.filter(event_ref=self.event_ref, device=self.device)

    def test_camera_motion_picture(self):

        with patch('notification.tasks.send_picture') as send_picture_mock:
            camera_motion_picture(self.in_data_motion)

            motion = self._get_motion()
            self.assertTrue(len(motion), 1)
            motion = motion[0]

            self.assertEqual(motion.motion_started_picture.name, 'path.png')
            self.assertFalse(motion.motion_ended_picture)

            kwargs = {
                'picture_path': self.motion_picture_path
            }

            send_picture_mock.apply_async.assert_called_once_with(kwargs=kwargs)

    def test_camera_motion_picture_no_more_motion(self):
        with patch('notification.tasks.send_picture') as send_picture:
            camera_motion_picture(self.in_data_motion)
            send_picture.reset_mock()
            camera_motion_picture(self.in_data_no_motion)

            motion = self._get_motion()
            self.assertTrue(len(motion), 1)
            motion = motion[0]

            self.assertEqual(motion.motion_started_picture.name, 'path.png')
            self.assertEqual(motion.motion_ended_picture.name, 'path2.png')

            kwargs = {
                'picture_path': self.no_motion_picture_path
            }

            send_picture.apply_async.assert_called_once_with(kwargs=kwargs)

    def test_no_motion_without_motion(self):
        with patch('notification.tasks.send_picture') as send_picture:
            with self.assertRaises(ValueError) as _context:
                camera_motion_picture(self.in_data_no_motion)

            motion = self._get_motion()
            self.assertEqual(0, len(motion))
            send_picture.assert_not_called()



    def test_no_motion_twice(self):
        with patch('notification.tasks.send_picture') as send_picture:
            camera_motion_picture(self.in_data_motion)
            send_picture.reset_mock()
            camera_motion_picture(self.in_data_no_motion)

            with self.assertRaises(ValueError) as _context:
                camera_motion_picture(self.in_data_no_motion)

            send_picture.assert_not_called()

    def test_motion_twice(self):
        with patch('notification.tasks.send_picture') as send_picture:
            camera_motion_picture(self.in_data_motion)

            with self.assertRaises(IntegrityError) as _context:
                camera_motion_picture(self.in_data_motion)

            motion = self._get_motion()
            self.assertEqual(1, len(motion))
            send_picture.assert_not_called()

