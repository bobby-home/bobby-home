import unittest
from decimal import Decimal
from http import HTTPStatus
from unittest.mock import patch, call

from django.forms import model_to_dict
from django.test import TransactionTestCase
from django.urls import reverse_lazy

from alarm.use_cases.out_alarm import NotifyAlarmStatus
from alarm.factories import AlarmStatusFactory
from camera.factories import CameraMotionDetectedPictureFactory, CameraROIFactory, CameraRectangleROIFactory
from alarm.models import AlarmStatus
from camera.models import CameraROI, CameraRectangleROI


class CameraROIViewsTestCase(TransactionTestCase):

    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory(running=True)
        self.device = self.alarm_status.device
        self.camera_roi: CameraROI = CameraROIFactory(device=self.alarm_status.device)

        # Until we do something better for the defined picture...
        self.camera_motion = CameraMotionDetectedPictureFactory(device=self.device)
