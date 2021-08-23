from devices.models import Device
import uuid
from unittest.mock import MagicMock, patch

from django.test import TransactionTestCase, TestCase
from django.utils import timezone

from alarm.use_cases.alarm_status import AlarmScheduleChangeStatus, AlarmChangeStatus, alarm_statuses_changed, change_statuses
from alarm.factories import AlarmScheduleFactory, AlarmStatusFactory
from alarm.models import AlarmSchedule, AlarmStatus, Ping
from camera.models import CameraMotionDetected
from devices.factories import DeviceFactory
from house.factories import HouseFactory


class AlarmStatusChangedTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_status: AlarmStatus = AlarmStatusFactory(running=False)
        self.device: Device = self.alarm_status.device

        return super().setUp()

    def _create_current_camera_motion(self):
        event_ref = str(uuid.uuid4())
        self.camera_motion_detected = CameraMotionDetected.objects.create(event_ref=event_ref, motion_started_at=timezone.now(), device=self.device)

    @patch("alarm.use_cases.alarm_status.can_turn_off")
    @patch("alarm.use_cases.alarm_status.integration_alarm_status_changed")
    def test_alarm_statuses_changed_should_not_call_integration(self, integration_alarm_status_changed: MagicMock, can_turn_off: MagicMock):
        can_turn_off.return_value = False
        alarm_statuses_changed([self.alarm_status])

        integration_alarm_status_changed.assert_not_called()

    @patch("alarm.use_cases.alarm_status.can_turn_off")
    @patch("alarm.use_cases.alarm_status.integration_alarm_status_changed")
    def test_alarm_statuses_changed_should_call_integration(self, integration_alarm_status_changed: MagicMock, can_turn_off: MagicMock):
        can_turn_off.return_value = True
        alarm_statuses_changed([self.alarm_status])
        integration_alarm_status_changed.assert_called_once_with(self.alarm_status)

    @patch("alarm.use_cases.alarm_status.can_turn_off")
    @patch("alarm.use_cases.alarm_status.integration_alarm_status_changed")
    def test_alarm_statuses_changed_force_should_call_integration(self, integration_alarm_status_changed: MagicMock, can_turn_off: MagicMock):
        can_turn_off.return_value = False
        alarm_statuses_changed([self.alarm_status], force=True)
        integration_alarm_status_changed.assert_called_once_with(self.alarm_status)


class ChangeStatusesTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()
        self.device1 = DeviceFactory()
        self.device2 = DeviceFactory()

        self.devices = [self.device1, self.device2]

        self.alarm_statuses = [
            AlarmStatusFactory(running=True, device=self.device1),
            AlarmStatusFactory(running=True, device=self.device2)
        ]

        for status in self.alarm_statuses:
            Ping.objects.create(
                device_id=status.device.device_id,
                service_name='object_detection',
                consecutive_failures=2,
                last_update=timezone.now()
            )

    def _reset_pings(self):
        pings = Ping.objects.filter(service_name='object_detection')

        devices = Device.objects.all()
        device_ids = [device.device_id for device in devices]

        for ping in pings:
            if ping.device_id in device_ids:
                self.assertEqual(ping.consecutive_failures, 0)
            else:
                self.assertEqual(ping.consecutive_failures, 2)

    def test_reset_pings(self):
        change_statuses(self.alarm_statuses)
        self._reset_pings()


class AlarmChangeStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()

        self.running_alarm_statuses = [
            AlarmStatusFactory(running=True),
            AlarmStatusFactory(running=True)
        ]

        super().setUp()

    def test_all_change_status(self):
        AlarmChangeStatus().all_change_statuses(False)
        statuses = AlarmStatus.objects.filter(running=False)
        self.assertEqual(2, len(statuses))

    def test_save_status(self):
        alarm_status = AlarmStatusFactory(running=False)
        alarm_status.running = True
        AlarmChangeStatus().save_status(alarm_status)
        verify = AlarmStatus.objects.get(pk=alarm_status.pk)
        self.assertEqual(verify.running, True)

    def test_reverse_status(self):
        AlarmChangeStatus().reverse_status(alarm_status_pk=self.running_alarm_statuses[0].pk)
        false_running = AlarmStatus.objects.get(pk=self.running_alarm_statuses[0].pk)
        true_running = AlarmStatus.objects.get(pk=self.running_alarm_statuses[1].pk)

        self.assertFalse(false_running.running)
        self.assertTrue(true_running.running)


class AlarmScheduleChangeStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()

        self.running_alarm_statuses = [
            AlarmStatusFactory(running=True),
            AlarmStatusFactory(running=True)
        ]

        self.schedule: AlarmSchedule = AlarmScheduleFactory()

        for status in self.running_alarm_statuses:
            self.schedule.alarm_statuses.add(status)

    def test_turn_off(self):
        change_status = AlarmScheduleChangeStatus()
        change_status.turn_off(self.schedule.uuid)
        cur_alarm_statuses = AlarmStatus.objects.all()

        for cur_alarm_status in cur_alarm_statuses:
            self.assertFalse(cur_alarm_status.running)

    def test_turn_on(self):
        change_status = AlarmScheduleChangeStatus()
        change_status.turn_on(self.schedule.uuid)
        cur_alarm_statuses = AlarmStatus.objects.all()

        for cur_alarm_status in cur_alarm_statuses:
            self.assertTrue(cur_alarm_status.running)

    def test_turn_off_motion_being(self):
        """
        Even if a motion is being detected, we change the database status.
        Its on the use_cases side that changes: don't tell to the service to actually turn off.
        """
        event_ref = str(uuid.uuid4())

        CameraMotionDetected.objects.create(event_ref=event_ref, motion_started_at=timezone.now(), device=self.running_alarm_statuses[0].device)

        change_status = AlarmScheduleChangeStatus()

        change_status.turn_off(self.schedule.uuid)

        alarm_statuses = AlarmStatus.objects.all()
        self.assertTrue(len(alarm_statuses), 2)

        self.assertFalse(alarm_statuses[0].running)
        self.assertFalse(alarm_statuses[1].running)

