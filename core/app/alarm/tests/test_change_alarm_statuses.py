import uuid

from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from alarm.business.alarm_change_status import AlarmScheduleChangeStatus, AlarmChangeStatus
from alarm.factories import AlarmScheduleFactory, AlarmStatusFactory
from alarm.models import AlarmSchedule, AlarmStatus, Ping
from camera.models import CameraMotionDetected
from devices.factories import DeviceFactory
from house.factories import HouseFactory


class ChangeStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()
        self.device1 = DeviceFactory()
        self.device2 = DeviceFactory()

        self.running_alarm_statuses = [
            AlarmStatusFactory(running=True, device=self.device1),
            AlarmStatusFactory(running=True, device=self.device2)
        ]

        Ping.objects.create(device_id=self.device1.device_id, service_name='object_detection', consecutive_failures=2, last_update=timezone.now())

    def test_reset_pings(self):
        AlarmChangeStatus().all_change_status(False)
        ping = Ping.objects.get(device_id=self.device1.device_id, service_name='object_detection')
        self.assertEqual(ping.consecutive_failures, 0)

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

    def test_set_alarm_status(self):
        change_status = AlarmScheduleChangeStatus()
        change_status.turn_off(self.schedule.uuid)
        cur_alarm_statuses = AlarmStatus.objects.all()

        for cur_alarm_status in cur_alarm_statuses:
            self.assertFalse(cur_alarm_status.running)

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

