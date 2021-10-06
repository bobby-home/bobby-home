from camera.messaging import HTTPCameraData
import unittest
import uuid
from unittest import skip
from unittest.mock import Mock, call, patch

from django.forms import model_to_dict
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from alarm.use_cases.out_alarm import NotifyAlarmStatus
from alarm.factories import AlarmStatusFactory, HTTPAlarmStatusFactory
from camera.factories import CameraROIFactoryConf
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetected
from devices.models import Device


class NotifyAlarmStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()
        self.device: Device = self.alarm_status.device

        self.alarm_messaging_mock = Mock()

    def _except_publish_alarm_status_call(self, http_camera_data=None):
        expected_calls = [call(self.device.device_id, self.alarm_status.running, http_camera_data)]
        self.alarm_messaging_mock.publish_alarm_status.assert_has_calls(expected_calls)

    def test_publish_false(self):
        self.alarm_status.running = False
        self.alarm_status.save()

        notify = NotifyAlarmStatus(self.alarm_messaging_mock)
        notify.publish_status_changed(self.device.id, self.alarm_status)

        self.alarm_messaging_mock.publish_alarm_status.assert_called_once()

        self._except_publish_alarm_status_call()

    def test_publish_http_alarm_status(self):
        self.alarm_status = HTTPAlarmStatusFactory()

        notify = NotifyAlarmStatus(self.alarm_messaging_mock)
        notify._publish(self.device, self.alarm_status)

        http = HTTPCameraData(
            user=self.alarm_status.user,
            password=self.alarm_status.password,
            endpoint=self.alarm_status.endpoint,
        )

        self._except_publish_alarm_status_call(http)

    @skip('moving this to camera motion test!')
    def test_publish_false_last_motion_being_done(self):
        """
            We have a motion unfinished (something went wrong...)
            But after that, we have a done motion (motion then no more motion).
            It should turn off the service.
        """
        self.alarm_status.running = False
        self.alarm_status.save()

        CameraMotionDetected.objects.create(
            event_ref=str(uuid.uuid4()),
            motion_started_at=timezone.now(),
            device=self.device)

        CameraMotionDetected.objects.create(
            event_ref=str(uuid.uuid4()),
            motion_started_at=timezone.now(),
            motion_ended_at=timezone.now(),
            device=self.device)

        notify = NotifyAlarmStatus(self.alarm_messaging_mock)
        notify.publish_status_changed(self.device.id, self.alarm_status)

        self._except_publish_alarm_status_call()

