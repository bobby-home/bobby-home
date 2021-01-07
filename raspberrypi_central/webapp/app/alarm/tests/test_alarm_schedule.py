from freezegun import freeze_time
from django.test import TestCase
from django.utils import timezone

from alarm.business.alarm import get_current_day
from alarm.factories import AlarmScheduleFactory
from alarm.models import AlarmSchedule
from house.factories import HouseFactory
from datetime import time
from django_celery_beat.models import PeriodicTask


class AlarmScheduleTestCase(TestCase):
    def setUp(self) -> None:
        HouseFactory()

    def test_delete_task(self):
        schedule = AlarmScheduleFactory()
        tasks = PeriodicTask.objects.all()

        self.assertEquals(len(tasks), 2)

        schedule.delete()
        tasks = PeriodicTask.objects.all()
        self.assertEquals(len(tasks), 0)


    @freeze_time("2020-12-21 03:21:00")
    def test_get_next_on(self):
        now = timezone.now()
        current_day = get_current_day(now)

        AlarmScheduleFactory(
            start_time=time(hour=now.hour, minute=now.minute -1),
            end_time=time(hour=now.hour, minute=now.minute +1),
            **{f'{current_day}': True})

        alarm_schedule = AlarmScheduleFactory(
            start_time=time(hour=now.hour, minute=now.minute +1),
            end_time=time(hour=now.hour, minute=now.minute +5),
            **{f'{current_day}': True})

        next_on = AlarmSchedule.objects.get_next_on()

        self.assertEqual(next_on, alarm_schedule)

    def test_get_next_off_empty(self):
        next_off = AlarmSchedule.objects.get_next_off()
        self.assertEqual(next_off, None)

    @freeze_time("2020-12-21 03:21:00")
    def test_get_next_off(self):
        now = timezone.now()
        current_day = get_current_day(now)

        alarm_schedule = AlarmScheduleFactory(
            start_time=time(hour=now.hour, minute=now.minute -1),
            end_time=time(hour=now.hour, minute=now.minute +1),
            **{f'{current_day}': True})

        alarm_schedule2 = AlarmScheduleFactory(
            start_time=time(hour=now.hour, minute=now.minute -1),
            end_time=time(hour=now.hour, minute=now.minute +2),
            **{f'{current_day}': True})

        next_off = AlarmSchedule.objects.get_next_off()

        self.assertEqual(next_off, alarm_schedule)
