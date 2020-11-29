from django.test import TestCase

from alarm.factories import AlarmScheduleFactory, AlarmStatusFactory
from alarm.models import AlarmSchedule, AlarmStatus
from alarm.tasks import set_alarm_status
from house.factories import HouseFactory


class ChangeAlarmStatusesTestCase(TestCase):
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
        set_alarm_status(self.schedule.uuid, False)

        cur_alarm_statuses = AlarmStatus.objects.all()

        for cur_alarm_status in cur_alarm_statuses:
            self.assertFalse(cur_alarm_status.running)

        set_alarm_status(self.schedule.uuid, True)
        cur_alarm_statuses = AlarmStatus.objects.all()

        for cur_alarm_status in cur_alarm_statuses:
            self.assertTrue(cur_alarm_status.running)
