from django.test import TestCase
# from rest_framework.test import APIClient
from django.urls import reverse
# from rest_framework import status
from devices.factories import DeviceFactory
from devices.models import Device
from . import models
from api_keys.factories import ApiKeysFactory
from api_keys.models import APIKey
from .communication.alarm import NotifyAlarmStatus
from .external.motion import save_motion
from .factories import CameraRectangleROIFactory, AlarmStatusFactory
from .models import CameraMotionDetected, CameraRectangleROI, AlarmStatus
from unittest.mock import patch, MagicMock


class SomeTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()
        self.device: Device = self.alarm_status.device

        self.roi1 = CameraRectangleROIFactory(device=self.device)
        self.roi2 = CameraRectangleROIFactory(device=self.device)

    # def test_save_motion(self):
    #     save_motion(self.device.device_id, {'rectangle': [self.roi1.id, self.roi2.id]})
    #
    #     motion = CameraMotionDetected.objects.filter(device__device_id=self.device.device_id)
    #     self.assertTrue(len(motion), 1)
    #
    #     rois = CameraRectangleROI.objects.filter(device=self.device)
    #     self.assertTrue(len(rois), 2)
    #
    #     rois_ids = [roi.id for roi in rois]
    #     self.assertEquals(rois_ids, [self.roi1.id, self.roi2.id])

    def test_save_motion_publish(self):
        with patch.object(NotifyAlarmStatus, 'publish', return_value=None) as mock:
            save_motion(self.device.device_id, {'rectangle': [self.roi1.id, self.roi2.id]})
            mock.assert_called_once()


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
