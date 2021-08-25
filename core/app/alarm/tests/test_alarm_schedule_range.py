from alarm.use_cases.alarm_status import AlarmChangeStatus
import json
from unittest.case import skip
from unittest.mock import MagicMock, patch
from django.utils import timezone

from freezegun.api import freeze_time
from alarm.use_cases.alarm_schedule_range import create_alarm_schedule_range, end_schedule_range, start_schedule_range, stop_current_alarm_schedule_range
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from alarm.models import AlarmSchedule, AlarmScheduleDateRange
from datetime import datetime, timedelta
from alarm.factories import AlarmScheduleFactory
from django.test import TestCase
from house.models import House
from alarm.business.alarm_schedule_range import get_current_schedule_range


class AlarmRangeScheduleBusinessTestCase(TestCase):
    def test_get_current_schedule_range_now(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now(),
           datetime_end=timezone.now() + timezone.timedelta(hours=5)
        )

        g = get_current_schedule_range()
        self.assertIsNotNone(g)

    def test_get_current_schedule_range_past(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() - timezone.timedelta(hours=1),
           datetime_end=timezone.now() + timezone.timedelta(hours=5)
        )

        g = get_current_schedule_range()
        self.assertIsNotNone(g)

    def test_get_current_schedule_range_not_found(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() + timezone.timedelta(hours=1),
           datetime_end=timezone.now() + timezone.timedelta(hours=5)
        )

        self.assertIsNone(get_current_schedule_range())

        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() - timezone.timedelta(hours=2),
           datetime_end=timezone.now() - timezone.timedelta(hours=1)
        )

        self.assertIsNone(get_current_schedule_range())

    def test_get_current_schedule_range_no_end(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() - timezone.timedelta(hours=1),
        )

        g = get_current_schedule_range()
        self.assertIsNotNone(g)


class AlarmScheduleRangeUseCasesTestCase(TestCase):
    def setUp(self):
        self.house = House(timezone='Europe/Paris')
        self.house.save()

    def _create_model_schedule_range(self, futur=True, end=True):
        if futur:
            start = timezone.now() + timezone.timedelta(hours=1)
        else:
            start = timezone.now()

        if end:
            datetime_end = timezone.now() + timezone.timedelta(hours=8)
        else:
            datetime_end = None

        schedule = AlarmScheduleDateRange(
            datetime_start=start,
            datetime_end=datetime_end
        )

        return schedule

    def _check_underlying_objects(self, past=False, end=True):
        schedules = AlarmScheduleDateRange.objects.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]

        tasks = []
        clocks = []

        if not past:
            turn_on_task = PeriodicTask.objects.get(task='alarm.start_schedule_range')
            self.assertEqual(schedule.turn_on_task, turn_on_task)
            turn_on_clock = ClockedSchedule.objects.get(clocked_time=schedule.datetime_start)
            self.assertEqual(turn_on_task.clocked, turn_on_clock)
            clocks.append(turn_on_clock)
            tasks.append(turn_on_task)

        if end:
            turn_off_task = PeriodicTask.objects.get(task='alarm.end_schedule_range')
            self.assertEqual(schedule.turn_off_task, turn_off_task)
            turn_off_clock = ClockedSchedule.objects.get(clocked_time=schedule.datetime_end)
            self.assertEqual(turn_off_task.clocked, turn_off_clock)
            clocks.append(turn_off_clock)
            tasks.append(turn_off_task)

        for task, cron in zip(tasks, clocks):
            self.assertEqual(task.args, json.dumps([str(schedule.uuid)]))
            self.assertEqual(task.clocked, cron)


    @freeze_time("2021-08-13 21:40:00")
    def test_create_schedule(self):
        schedule = self._create_model_schedule_range()
        create_alarm_schedule_range(schedule)
        self._check_underlying_objects()

    @freeze_time("2021-08-13 21:40:00")
    def test_create_schedule_no_end(self):
        schedule = self._create_model_schedule_range(end=False)
        create_alarm_schedule_range(schedule)
        self._check_underlying_objects(end=False)

    @patch('alarm.tasks.start_schedule_range')
    def test_create_schedule_start_now(self, start_schedule_range_mock: MagicMock):
        schedule = self._create_model_schedule_range(futur=False)
        create_alarm_schedule_range(schedule)

        self._check_underlying_objects(past=True)

        start_schedule_range_mock.assert_called_once_with(None)

    @freeze_time("2021-08-14 17:45:00")
    @patch('alarm.tasks.end_schedule_range')
    def test_stop_current_alarm_schedule_range(self, end_schedule_range_mock):
        schedule = self._create_model_schedule_range(futur=False)
        schedule.save()
        updated_schedule = stop_current_alarm_schedule_range()
        self.assertIsNotNone(updated_schedule)

        db_schedule = AlarmScheduleDateRange.objects.all()
        self.assertEqual(1, len(db_schedule))
        db_schedule = db_schedule[0]

        self.assertEqual(db_schedule.datetime_end, timezone.now())
        end_schedule_range_mock.assert_called_once_with(str(schedule.uuid))

        self.assertIsNone(db_schedule.turn_off_task)

        tasks = PeriodicTask.objects.all()
        self.assertEqual(0, len(tasks))

    @patch('alarm.use_cases.alarm_schedule_range.disable_all_schedules')
    @patch('alarm.use_cases.alarm_schedule_range.AlarmChangeStatus', spec_set=AlarmChangeStatus)
    def test_start_schedule_range(self, AlarmChangeStatusMock: MagicMock, disable_all_schedules_mock: MagicMock):
        start_schedule_range()
        disable_all_schedules_mock.assert_called_once_with()
        AlarmChangeStatusMock.all_change_statuses.assert_called_once_with(True)

    @patch('alarm.use_cases.alarm_schedule_range.enable_all_schedules')
    @patch('alarm.use_cases.alarm_schedule_range.AlarmChangeStatus', spec_set=AlarmChangeStatus)
    def test_end_schedule_range(self, AlarmChangeStatusMock: MagicMock, enable_all_schedules: MagicMock):
        end_schedule_range()
        enable_all_schedules.assert_called_once_with()
        AlarmChangeStatusMock.all_change_statuses.assert_called_once_with(False)
