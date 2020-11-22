from decimal import Decimal
from http import HTTPStatus
from unittest.mock import patch, call

from django.forms import model_to_dict
from django.test import TransactionTestCase
from django.urls import reverse_lazy

from alarm.communication.out_alarm import NotifyAlarmStatus
from alarm.factories import AlarmStatusFactory, CameraROIFactory, CameraMotionDetectedPictureFactory, \
    CameraRectangleROIFactory
from alarm.models import AlarmStatus, CameraROI, CameraRectangleROI


class CameraROIViewsTestCase(TransactionTestCase):

    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory(running=True)
        self.device = self.alarm_status.device
        self.camera_roi: CameraROI = CameraROIFactory(device=self.alarm_status.device)

        # Until we do something better for the defined picture...
        self.camera_motion = CameraMotionDetectedPictureFactory(device=self.device)


    def test_create(self):
        self.camera_roi.delete()

        self.camera_rectangle_rois = [
            CameraRectangleROI(x=Decimal(249), y=Decimal(120), w=Decimal(226), h=Decimal(293)),
            CameraRectangleROI(x=Decimal(56), y=Decimal(36), w=Decimal(72), h=Decimal(111)),
        ]

        payload = {
            "device": self.device.id,
            "form-TOTAL_FORMS": "2", "form-INITIAL_FORMS": "0", "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-x": self.camera_rectangle_rois[0].x, "form-0-y": self.camera_rectangle_rois[0].y, "form-0-w": self.camera_rectangle_rois[0].w, "form-0-h": self.camera_rectangle_rois[0].h,
            "form-1-x": self.camera_rectangle_rois[1].x, "form-1-y": self.camera_rectangle_rois[1].y, "form-1-w": self.camera_rectangle_rois[1].w, "form-1-h": self.camera_rectangle_rois[1].h
        }

        with patch.object(NotifyAlarmStatus, 'publish_roi_changed', return_value=None) as mock:
            response = self.client.post(reverse_lazy('alarm:camera_roi-add'), payload)

            self.assertEqual(response.status_code, HTTPStatus.FOUND)

            camera_rois = CameraROI.objects.filter(device=self.device)
            self.assertEqual(len(camera_rois), 1)
            camera_roi = camera_rois[0]

            rectangle_rois = CameraRectangleROI.objects.filter(camera_roi=camera_roi)
            self.assertEqual(len(rectangle_rois), 2)

            rectangle_rois_dict = [model_to_dict(roi, exclude=('camera_roi', 'id')) for roi in rectangle_rois]
            expected_rois_dict = [model_to_dict(roi, exclude=('camera_roi', 'id')) for roi in self.camera_rectangle_rois]

            self.assertEqual(rectangle_rois_dict, expected_rois_dict)

            mock.assert_called_once()


    def test_delete(self):
        CameraRectangleROIFactory(camera_roi=self.camera_roi)
        CameraRectangleROIFactory(camera_roi=self.camera_roi)

        with patch.object(NotifyAlarmStatus, 'publish_roi_changed', return_value=None) as mock:
            response = self.client.post(reverse_lazy('alarm:camera_roi-delete', kwargs={'pk': self.camera_roi.id}))
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

            camera_rois = CameraROI.objects.filter(device=self.device)
            self.assertEqual(len(camera_rois), 0)

            rectangle_rois = CameraRectangleROI.objects.filter(camera_roi=self.camera_roi)
            self.assertEqual(len(rectangle_rois), 0)

            mock.assert_called_once()

            expected_call = [call(self.alarm_status.pk, None)]
            mock.assert_has_calls(expected_call)


    def test_edit(self):
        CameraRectangleROIFactory(camera_roi=self.camera_roi)
        CameraRectangleROIFactory(camera_roi=self.camera_roi)

        camera_rectangle_rois = [
            CameraRectangleROI(x=Decimal(249), y=Decimal(120), w=Decimal(226), h=Decimal(293), camera_roi=self.camera_roi),
            CameraRectangleROI(x=Decimal(56), y=Decimal(36), w=Decimal(72), h=Decimal(111), camera_roi=self.camera_roi),
        ]

        payload = {
            "form-TOTAL_FORMS": "2", "form-INITIAL_FORMS": "0", "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-x": camera_rectangle_rois[0].x, "form-0-y": camera_rectangle_rois[0].y, "form-0-w": camera_rectangle_rois[0].w, "form-0-h": camera_rectangle_rois[0].h,
            "form-1-x": camera_rectangle_rois[1].x, "form-1-y": camera_rectangle_rois[1].y, "form-1-w": camera_rectangle_rois[1].w, "form-1-h": camera_rectangle_rois[1].h
        }

        with patch.object(NotifyAlarmStatus, 'publish_roi_changed', return_value=None) as mock:
            response = self.client.post(reverse_lazy('alarm:camera_roi-edit', kwargs={'pk': self.camera_roi.id}), payload)

            camera_rois = CameraROI.objects.filter(device=self.device)
            self.assertEqual(len(camera_rois), 1)
            camera_roi = camera_rois[0]
            self.assertEqual(camera_roi, self.camera_roi)

            self.assertEqual(response.status_code, HTTPStatus.FOUND)

            rectangle_rois = CameraRectangleROI.objects.filter(camera_roi=self.camera_roi, disabled=False)
            self.assertEqual(len(rectangle_rois), 2)

            disabled_rectangle_rois = CameraRectangleROI.objects.filter(camera_roi=self.camera_roi, disabled=True)
            self.assertEqual(len(disabled_rectangle_rois), 2)

            rectangles = [model_to_dict(instance) for instance in rectangle_rois]

            expected_call = [call(self.alarm_status.pk,self.camera_roi, rectangles)]
            mock.assert_called_once()

            mock.assert_has_calls(expected_call)

            rectangle_rois_dict = [model_to_dict(roi, exclude=('camera_roi', 'id')) for roi in rectangle_rois]
            expected_rois_dict = [model_to_dict(roi, exclude=('camera_roi', 'id')) for roi in camera_rectangle_rois]

            self.assertEqual(rectangle_rois_dict, expected_rois_dict)
