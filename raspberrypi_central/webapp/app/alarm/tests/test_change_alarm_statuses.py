import uuid

from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from alarm.business.alarm_schedule_change_status import AlarmScheduleChangeStatus
from alarm.factories import AlarmScheduleFactory, AlarmStatusFactory
from alarm.models import AlarmSchedule, AlarmStatus
from camera.models import CameraMotionDetected
from house.factories import HouseFactory


class ChangeAlarmStatusesTestCase(TransactionTestCase):
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
        Its on the communication side that changes: don't tell to the service to actually turn off.
        """
        event_ref = str(uuid.uuid4())

        CameraMotionDetected.objects.create(event_ref=event_ref, motion_started_at=timezone.now(), device=self.running_alarm_statuses[0].device)

        change_status = AlarmScheduleChangeStatus()

        change_status.turn_off(self.schedule.uuid)

        alarm_statuses = AlarmStatus.objects.all()
        self.assertTrue(len(alarm_statuses), 2)

        self.assertFalse(alarm_statuses[0].running)
        self.assertFalse(alarm_statuses[1].running)
