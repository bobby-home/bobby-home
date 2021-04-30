import dataclasses
from alarm.use_cases.data import Detection
import uuid
from decimal import Decimal

from django.forms import model_to_dict
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from alarm.business.in_motion import save_motion
from alarm.factories import AlarmStatusFactory
from camera.factories import CameraROIFactory, CameraRectangleROIFactory
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetectedBoundingBox, CameraMotionDetected, CameraRectangleROI
from devices.models import Device


class SaveMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()
        self.device: Device = self.alarm_status.device
        self.event_ref = str(uuid.uuid4())

    def test_save_motion(self):
        start_motion_time = timezone.now()

        with freeze_time(start_motion_time):
            save_motion(self.device, [], self.event_ref, True)
            motion = CameraMotionDetected.objects.filter(device__device_id=self.device.device_id)
            self.assertTrue(motion.exists())
            motion = motion[0]

            self.assertEqual(motion.motion_started_at, start_motion_time)
            self.assertEqual(str(motion.event_ref), self.event_ref)
            self.assertIsNone(motion.motion_ended_at)

        end_motion_time = timezone.now()
        with freeze_time(end_motion_time):
            save_motion(self.device, [], self.event_ref, False)
            motion = CameraMotionDetected.objects.get(device__device_id=self.device.device_id)
            self.assertEqual(motion.motion_started_at, start_motion_time)
            self.assertEqual(motion.motion_ended_at, end_motion_time)
            self.assertEqual(str(motion.event_ref), self.event_ref)


    def test_save_motion_rectangles(self):
        detections = (
            Detection(
                bounding_box=[],
                bounding_box_point_and_size={'x': 10, 'y': 15, 'w': 200, 'h': 150},
                class_id='people',
                score=0.8
            ),
        )

        save_motion(self.device, detections, self.event_ref, True)

        motions = CameraMotionDetected.objects.filter(device__device_id=self.device.device_id)
        self.assertTrue(len(motions), 1)
        motion = motions[0]

        bounding_boxes = CameraMotionDetectedBoundingBox.objects.filter(camera_motion_detected=motion)
        self.assertTrue(len(bounding_boxes), len(detections))
        bounding_box = bounding_boxes[0]

        for bounding_box, detection in zip(bounding_boxes, detections):
            detection_plain = dataclasses.asdict(detection)
            expected_bounding_box = detection_plain['bounding_box_point_and_size']
            expected_bounding_box['score'] = detection.score
            
            self.assertEqual(
                model_to_dict(bounding_box, exclude=('camera_motion_detected', 'id')),
                expected_bounding_box
            )

