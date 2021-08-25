from django.utils import timezone
from camera.models import CameraMotionDetected
import uuid
from alarm.business.alarm_status import can_turn_off
from devices.factories import DeviceFactory
from django.test.testcases import TestCase


class CanTurnOffTestCase(TestCase):
    def setUp(self) -> None:
        self.device = DeviceFactory()
        return super().setUp()

    def _create_camera_motion(self, current=True):
        event_ref = str(uuid.uuid4())
        motion_ended_at = None if current else timezone.now()

        self.camera_motion_detected = CameraMotionDetected.objects.create(
            event_ref=event_ref,
            motion_started_at=timezone.now(),
            motion_ended_at=motion_ended_at,
            device=self.device)

    def test_can_turn_off(self):
        self._create_camera_motion(False)
        self.assertTrue(can_turn_off(self.device))

    def test_cannot_turn_off_motion_being(self):
         self._create_camera_motion()
         self.assertFalse(can_turn_off(self.device))

