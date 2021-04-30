import uuid
from unittest import skip
from unittest.mock import Mock, call, patch

from django.forms import model_to_dict
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from alarm.use_cases.out_alarm import NotifyAlarmStatus
from alarm.factories import AlarmStatusFactory
from camera.factories import CameraROIFactoryConf 
from alarm.models import AlarmStatus
from camera.models import CameraMotionDetected
from devices.models import Device


class NotifyAlarmStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory()
        self.device: Device = self.alarm_status.device

        self.alarm_messaging_mock = Mock()

    def _except_publish_alarm_status_call(self):
        expected_payload = {'is_dumb': self.alarm_status.is_dumb}
        expected_calls = [call(self.device.device_id, self.alarm_status.running, self.alarm_status.is_dumb, expected_payload)]
        self.alarm_messaging_mock.publish_alarm_status.assert_has_calls(expected_calls)

    def test_publish_false(self):
        self.alarm_status.running = False
        self.alarm_status.save()

        notify = NotifyAlarmStatus(self.alarm_messaging_mock)
        notify.publish_status_changed(self.device.id, self.alarm_status)

        self.alarm_messaging_mock.publish_alarm_status.assert_called_once()

        self._except_publish_alarm_status_call()

    def test_no_publish_motion_being(self):
        self.alarm_status.running = False
        self.alarm_status.save()

        event_ref = str(uuid.uuid4())

        CameraMotionDetected.objects.create(event_ref=event_ref, motion_started_at=timezone.now(), device=self.device)

        notify = NotifyAlarmStatus(self.alarm_messaging_mock)
        notify.publish_status_changed(self.device.id, self.alarm_status)

        self.alarm_messaging_mock.publish_alarm_status.assert_not_called()

    def test_force_publish_motion_being(self):
        self.alarm_status.running = False
        self.alarm_status.save()
        event_ref = str(uuid.uuid4())

        CameraMotionDetected.objects.create(event_ref=event_ref, motion_started_at=timezone.now(), device=self.device)

        notify = NotifyAlarmStatus(self.alarm_messaging_mock)
        notify.publish_status_changed(self.device.id, self.alarm_status, force=True)
        self._except_publish_alarm_status_call()

    def test_publish_false_motion_ended(self):
        self.alarm_status.running = False
        self.alarm_status.save()

        event_ref = str(uuid.uuid4())

        CameraMotionDetected.objects.create(
            event_ref=event_ref,
            motion_started_at=timezone.now(),
            motion_ended_at=timezone.now(),
            device=self.device)

        notify = NotifyAlarmStatus(self.alarm_messaging_mock)
        notify.publish_status_changed(self.device.id, self.alarm_status)
        self._except_publish_alarm_status_call()

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

