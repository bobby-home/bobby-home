from django.test import TestCase
from django.utils import timezone

from alarm.factories import CameraMotionDetectedFactory
from camera.business.camera_motion import close_unclosed_camera_motions
from camera.models import CameraMotionDetected
from devices.factories import DeviceFactory


class CameraMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        self.motions = [
            CameraMotionDetectedFactory(device=self.device),
            CameraMotionDetectedFactory(device=self.device),
            CameraMotionDetectedFactory(device=self.device),
            CameraMotionDetectedFactory(device=self.device),
        ]

    def test_close_unclosed_camera_motions(self):
        close_unclosed_camera_motions(self.device.device_id)
        for motion in CameraMotionDetected.objects.all():
            self.assertTrue(motion.closed_by_system)

    def test_dont_close_closed_camera_motions(self):
        closed = CameraMotionDetectedFactory(device=self.device, motion_ended_at=timezone.now())
        close_unclosed_camera_motions(self.device.device_id)

        motion = CameraMotionDetected.objects.get(pk=closed.pk)
        self.assertFalse(motion.closed_by_system)
