import uuid
from decimal import Decimal
from unittest import skip

from django.forms import model_to_dict
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from alarm.communication.alarm_consts import ROITypes
from alarm.communication.in_motion import save_motion
from alarm.factories import AlarmStatusFactory, CameraROIFactory, CameraRectangleROIFactory
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetectedBoundingBox, CameraMotionDetected, CameraRectangleROI
from devices.models import Device


class SaveMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()
        self.device: Device = self.alarm_status.device

        self.roi = CameraROIFactory(device=self.device)

        self.roi1 = CameraRectangleROIFactory(camera_roi=self.roi)
        self.roi2 = CameraRectangleROIFactory(camera_roi=self.roi)

    def test_save_motion(self):
        event_ref = str(uuid.uuid4())

        start_motion_time = timezone.now()
        with freeze_time(start_motion_time):
            save_motion(self.device.device_id, {}, event_ref, True)
            motion = CameraMotionDetected.objects.filter(device__device_id=self.device.device_id)
            self.assertTrue(motion.exists())
            motion = motion[0]

            self.assertEqual(motion.motion_started_at, start_motion_time)
            self.assertEqual(str(motion.event_ref), event_ref)
            self.assertIsNone(motion.motion_ended_at)

        end_motion_time = timezone.now()
        with freeze_time(end_motion_time):
            save_motion(self.device.device_id, {}, event_ref, False)
            motion = CameraMotionDetected.objects.get(device__device_id=self.device.device_id)
            self.assertEqual(motion.motion_started_at, start_motion_time)
            self.assertEqual(motion.motion_ended_at, end_motion_time)
            self.assertEqual(str(motion.event_ref), event_ref)


    def test_save_motion_rectangles(self):
        seen_in = {
            ROITypes.RECTANGLES.value: {
                'ids': [self.roi1.id, self.roi2.id],
                'bounding_box': {'x': Decimal(10), 'y': Decimal(15), 'w': Decimal(200), 'h': Decimal(150)}
            }
        }

        save_motion(self.device.device_id, seen_in, str(uuid.uuid4()), True)

        motions = CameraMotionDetected.objects.filter(device__device_id=self.device.device_id)
        self.assertTrue(len(motions), 1)
        motion = motions[0]

        rois = CameraRectangleROI.objects.filter(camera_roi__device=self.device)
        self.assertTrue(len(rois), 2)

        rois_ids = [roi.id for roi in rois]
        self.assertEquals(rois_ids, [self.roi1.id, self.roi2.id])

        bounding_boxes = CameraMotionDetectedBoundingBox.objects.filter(camera_motion_detected=motion)
        self.assertTrue(len(bounding_boxes), 1)
        bounding_box = bounding_boxes[0]

        self.assertEqual(
            model_to_dict(bounding_box, exclude=('camera_motion_detected', 'id')),
            seen_in[ROITypes.RECTANGLES.value]['bounding_box']
        )

    def test_save_motion_full(self):
        seen_in = {
            ROITypes.FULL.value: {
                'ids': [self.roi1.id, self.roi2.id],
                'bounding_box': {'x': Decimal(10), 'y': Decimal(15), 'w': Decimal(200), 'h': Decimal(150)}
            }
        }

        save_motion(self.device.device_id, seen_in, str(uuid.uuid4()), True)

        motions = CameraMotionDetected.objects.filter(device__device_id=self.device.device_id)
        self.assertTrue(len(motions), 1)
        motion = motions[0]

        bounding_boxes = CameraMotionDetectedBoundingBox.objects.filter(camera_motion_detected=motion)
        self.assertTrue(len(bounding_boxes), 1)
        bounding_box = bounding_boxes[0]

        self.assertEqual(
            model_to_dict(bounding_box, exclude=('camera_motion_detected', 'id')),
            seen_in[ROITypes.FULL.value]['bounding_box']
        )
