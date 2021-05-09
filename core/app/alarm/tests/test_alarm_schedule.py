from alarm.use_cases.alarm_schedule import create_alarm_schedule, update_alarm_schedule
from alarm.use_cases.alarm_status import alarm_statuses_changed
from freezegun import freeze_time
from django.test import TestCase
from django.utils import timezone

from alarm.business.alarm_schedule import get_current_day
from alarm.factories import AlarmScheduleFactory, AlarmStatusFactory
from alarm.models import AlarmSchedule
from house.factories import HouseFactory
from datetime import time
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class UseCaseAlarmScheduleTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_statuses = [
            AlarmStatusFactory(),
            AlarmStatusFactory()
        ]

        return super().setUp()

    def _check_underlying_objects(self):
        schedules = AlarmSchedule.objects.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]

        periodic_tasks = PeriodicTask.objects.all()
        self.assertEqual(len(periodic_tasks), 2)

        turn_on_task = PeriodicTask.objects.get(task='alarm.set_alarm_on')
        turn_off_task = PeriodicTask.objects.get(task='alarm.set_alarm_off')

        self.assertEqual(schedule.turn_on_task, turn_on_task)
        self.assertEqual(schedule.turn_off_task, turn_off_task)

        cons = CrontabSchedule.objects.all()
        self.assertEqual(len(cons), 2)

        turn_on_cron = CrontabSchedule.objects.get(minute='00', hour='06')
        turn_off_cron = CrontabSchedule.objects.get(minute='00', hour='08')

        self.assertEqual(turn_off_task.crontab, turn_off_cron)
        self.assertEqual(turn_on_task.crontab, turn_on_cron)

    def test_create_alarm_schedule(self):
        schedule = AlarmSchedule(
            start_time='06:00',
            end_time='08:00',
            monday=True,
            tuesday=False,
            wednesday=True,
            thursday=False,
            friday=True,
            saturday=False
            sunday=True,
            alarm_statuses=self.alarm_statuses
        )

        create_alarm_schedule(schedule)
        self._check_underlying_objects()

    def test_update_alarm_schedule(self):
        schedule = AlarmScheduleFactory()
        
        schedule.start_time = '04:15'
        schedule.end_time = '09:30'

        update_alarm_schedule(schedule)
        
        # wip: I'm here, I'll continue tomorrow.
        self._check_underlying_objects()

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
