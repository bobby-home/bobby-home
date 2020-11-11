import uuid
from decimal import Decimal
from http import HTTPStatus

from django.forms import model_to_dict
from django.test import TestCase, TransactionTestCase
from django.urls import reverse, reverse_lazy
# from rest_framework import status
from unittest.mock import Mock, call, patch
from unittest import skip

from devices.models import Device
from .communication.alarm import NotifyAlarmStatus, notify_alarm_status_factory
from .external.motion import save_motion
from .factories import CameraRectangleROIFactory, AlarmStatusFactory, CameraROIFactory, \
    CameraMotionDetectedPictureFactory
from .models import CameraMotionDetected, CameraRectangleROI, AlarmStatus, CameraROI

# def assert_model_instance_fields_equal(model, expected, actual):
#     for field_name in model._meta.get_fields():
#         expected_value = getattr(expected, field_name)
#         actual_value = getattr(actual, field_name)
#         self.assertEqual(expected_value, actual_value)
from .models.camera import CameraMotionDetectedBoundingBox


class NotifyAlarmStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()
        self.device: Device = self.alarm_status.device

        self.roi = CameraROIFactory(device=self.device)

        self.roi1 = CameraRectangleROIFactory(camera_roi=self.roi)
        self.roi2 = CameraRectangleROIFactory(camera_roi=self.roi)

        self.alarm_messaging_factory_mock = Mock()
        self.alarm_messaging_mock = Mock()
        self.alarm_messaging_factory_mock.return_value = self.alarm_messaging_mock
        self.get_mqtt_client_mock = Mock()

    def test_publish_false(self):
        notify = NotifyAlarmStatus(self.alarm_messaging_factory_mock, self.get_mqtt_client_mock)
        notify.publish_status_changed(self.device.id, False)

        self.alarm_messaging_mock.publish_alarm_status.assert_called_once()

        expected_calls = [call(self.device.device_id, False, None)]
        self.alarm_messaging_mock.publish_alarm_status.assert_has_calls(expected_calls)

    def test_publish_true_with_roi(self):
        notify = NotifyAlarmStatus(self.alarm_messaging_factory_mock, self.get_mqtt_client_mock)
        notify.publish_status_changed(self.device.id, True)

        self.alarm_messaging_mock.publish_alarm_status.assert_called_once()

        expected_calls = [call(self.device.device_id, True, [model_to_dict(self.roi1), model_to_dict(self.roi2)])]
        self.alarm_messaging_mock.publish_alarm_status.assert_has_calls(expected_calls)

    def test_publish_roi_changed_false(self):
        self.alarm_status.running = False
        self.alarm_status.save()

        fake_roi = [{}, {}]
        notify = NotifyAlarmStatus(self.alarm_messaging_factory_mock, self.get_mqtt_client_mock)
        notify.publish_roi_changed(self.device.id, fake_roi)

        self.alarm_messaging_mock.publish_alarm_status.assert_not_called()

    def test_publish_roi_changed_true_with_roi(self):
        self.alarm_status.running = True
        self.alarm_status.save()

        fake_roi = [{}, {}]
        notify = NotifyAlarmStatus(self.alarm_messaging_factory_mock, self.get_mqtt_client_mock)
        notify.publish_roi_changed(self.device.id, fake_roi)

        self.alarm_messaging_mock.publish_alarm_status.assert_called_once()

        expected_calls = [call(self.device.device_id, True, fake_roi)]
        self.alarm_messaging_mock.publish_alarm_status.assert_has_calls(expected_calls)


class NotifyAlarmStatusCalledTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()

    def test_notify_when_status_change(self):
        with patch.object(NotifyAlarmStatus, 'publish_status_changed', return_value=None) as mock:
            self.alarm_status.running = False
            self.alarm_status.save()

            expected_call = [call(self.alarm_status.pk, False)]
            mock.assert_called_once()
            mock.assert_has_calls(expected_call)

            mock.reset_mock()

            self.alarm_status.running = True
            self.alarm_status.save()

            expected_call = [call(self.alarm_status.pk, True)]
            mock.assert_called_once()
            mock.assert_has_calls(expected_call)


class SaveMotionTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()
        self.device: Device = self.alarm_status.device

        self.roi = CameraROIFactory(device=self.device)

        self.roi1 = CameraRectangleROIFactory(camera_roi=self.roi)
        self.roi2 = CameraRectangleROIFactory(camera_roi=self.roi)

    def test_save_motion(self):
        # TODO WARNING: the smart camera send us ymin, xmin, ymax, xmax not x y h w !!!
        seen_in = {
            'rectangle': {
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
            seen_in['rectangle']['bounding_box']
        )


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

            rectangle_rois = CameraRectangleROI.objects.filter(camera_roi=self.camera_roi)
            self.assertEqual(len(rectangle_rois), 2)

            rectangles = [model_to_dict(instance) for instance in rectangle_rois]

            expected_call = [call(self.alarm_status.pk, rectangles)]
            mock.assert_called_once()

            mock.assert_has_calls(expected_call)

            rectangle_rois_dict = [model_to_dict(roi, exclude=('camera_roi', 'id')) for roi in rectangle_rois]
            expected_rois_dict = [model_to_dict(roi, exclude=('camera_roi', 'id')) for roi in camera_rectangle_rois]

            self.assertEqual(rectangle_rois_dict, expected_rois_dict)


# class AlarmViewTestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         ApiKeysFactory()
#         self.key = APIKey.objects.get(pk=1)
#
#     def test_create(self):
#         print(f'key={self.key.key}')
#
#         res1 = self.client.post(
#             reverse('alarmstatus-list'),
#             {'running': True},
#             format="json",
#             **{'HTTP_API_KEY': self.key.key})
#
#         self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(res1.data, {'running': True})
#
#         self.assertEqual(models.AlarmStatus.objects.count(), 1)
#         self.assertEqual(models.AlarmStatus.objects.get().running, True)
#
#         res_get = self.client.get(reverse('alarmstatus-list'), **{'HTTP_API_KEY': self.key.key})
#         self.assertEqual(res_get.status_code, status.HTTP_200_OK)
#         # self.assertEqual(res_get.data, {'id': 1, 'running': True})
#
#         res2 = self.client.post(
#             reverse('alarmstatus-list'),
#             {'running': False},
#             format="json",
#              **{'HTTP_API_KEY': self.key.key})
#
#         self.assertEqual(res2.data, {'running': False})
#         self.assertEqual(models.AlarmStatus.objects.count(), 1)
#         self.assertEqual(models.AlarmStatus.objects.get().running, False)
