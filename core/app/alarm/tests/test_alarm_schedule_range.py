import json
from unittest.case import skip
from unittest.mock import MagicMock, patch
from django.utils import timezone

from freezegun.api import freeze_time
from alarm.use_cases.alarm_range_schedule import create_alarm_range_schedule, end_schedule_range, start_schedule_range, stop_current_alarm_range_schedule
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from alarm.models import AlarmSchedule, AlarmScheduleDateRange
from datetime import datetime, timedelta
from alarm.factories import AlarmScheduleFactory
from django.test import TestCase
from house.models import House


class AlarmScheduleDateRangeTestCase(TestCase):
    def setUp(self):
        self.house = House(timezone='Europe/Paris')
        self.house.save()

    @skip
    def test_create_schedule(self):
        alarm_schedule = AlarmScheduleFactory()

        data = {
            'datetime_start': datetime.now(),
            'datetime_end': datetime.now(),
        }

        alarm_schedule = AlarmScheduleDateRange(**data)
        alarm_schedule.save()

        to_test = {
            'start': alarm_schedule.turn_on_task,
            'end': alarm_schedule.turn_off_task
        }

        for key, value in to_test.items():
            self.assertEqual(value.clocked.clocked_time, data[f'datetime_{key}'])

        all_schedules = AlarmSchedule.objects.all()

        for schedule in all_schedules:
            self.assertEqual(schedule.turn_on_task.enabled, False)
            self.assertEqual(schedule.turn_off_task.enabled, False)

        alarm_schedule.delete()
        all_schedules = AlarmSchedule.objects.all()

        for schedule in all_schedules:
            self.assertEqual(schedule.turn_on_task.enabled, True)
            self.assertEqual(schedule.turn_off_task.enabled, True)


class AlarmScheduleModelTestCase(TestCase):
    def setUp(self):
        self.house = House(timezone='Europe/Paris')
        self.house.save()

    def _create_model_schedule_range(self, futur=True):
        if futur:
            start = timezone.now() + timezone.timedelta(hours=1) 
        else:
            start = timezone.now()

        schedule = AlarmScheduleDateRange(
            datetime_start=start,
            datetime_end=timezone.now() + timezone.timedelta(hours=8),
        )

        return schedule

    def _check_underlying_objects(self):
        schedules = AlarmScheduleDateRange.objects.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]

        periodic_tasks = PeriodicTask.objects.all()
        self.assertEqual(len(periodic_tasks), 2)

        turn_on_task = PeriodicTask.objects.get(task='alarm.start_schedule_range')
        turn_off_task = PeriodicTask.objects.get(task='alarm.end_schedule_range')

        self.assertEqual(schedule.turn_on_task, turn_on_task)
        self.assertEqual(schedule.turn_off_task, turn_off_task)

        turn_on_clock = ClockedSchedule.objects.get(clocked_time=schedule.datetime_start)
        turn_off_clock = ClockedSchedule.objects.get(clocked_time=schedule.datetime_end)

        for task, cron in zip([turn_off_task, turn_on_task], [turn_off_clock, turn_on_clock]):
            self.assertEqual(task.args, json.dumps([str(schedule.uuid)]))
            self.assertEqual(task.clocked, cron)

        cons = ClockedSchedule.objects.all()
        self.assertEqual(len(cons), 2)

        # no timezone for ClockedSchedule, how does it work?? UTC?? TZ in datetime ????
        #for clocked in [turn_on_clocked, turn_off_clocked]:
        #    self.assertEqual(str(cron.timezone), self.house.timezone)

        self.assertEqual(turn_off_task.clocked, turn_off_clock)
        self.assertEqual(turn_on_task.clocked, turn_on_clock)


    @freeze_time("2021-08-13 21:40:00")
    def test_create_schedule(self):
        schedule = self._create_model_schedule_range()
        create_alarm_range_schedule(schedule)
        self._check_underlying_objects()

    @patch('alarm.tasks.start_schedule_range')
    def test_create_schedule_start_now(self, start_schedule_range_mock: MagicMock):
        schedule = self._create_model_schedule_range(futur=False)
        create_alarm_range_schedule(schedule)

        schedules = AlarmScheduleDateRange.objects.all()
        self.assertEqual(len(schedules), 1)
 
        periodic_tasks = PeriodicTask.objects.all()
        self.assertEqual(len(periodic_tasks), 0)
        
        start_schedule_range_mock.assert_called_once_with(None)

    @freeze_time("2021-08-14 17:45:00")
    def test_stop_current_alarm_range_schedule(self):
        schedule = self._create_model_schedule_range(futur=False)
        schedule.save()
        updated_schedule = stop_current_alarm_range_schedule()
        self.assertIsNotNone(updated_schedule)

        db_schedule = AlarmScheduleDateRange.objects.all()
        self.assertEqual(1, len(db_schedule))
        db_schedule = db_schedule[0]

        self.assertEqual(db_schedule.datetime_end, timezone.now())

    @patch('alarm.tasks.end_schedule_range')
    def test_stop_current_alarm_range_schedule_delete_turn_off_task(self, end_schedule_range_mock):
        schedule = self._create_model_schedule_range(futur=False)
        create_alarm_range_schedule(schedule)
        updated_schedule = stop_current_alarm_range_schedule()
        self.assertIsNotNone(updated_schedule)

        db_schedule = AlarmScheduleDateRange.objects.all()
        self.assertEqual(1, len(db_schedule))
        db_schedule = db_schedule[0]
        
        self.assertIsNone(db_schedule.turn_off_task)
        end_schedule_range_mock.assert_called_once_with(str(schedule.uuid))

    @patch('alarm.use_cases.alarm_range_schedule.disable_all_schedules')
    @patch('alarm.use_cases.alarm_range_schedule.AlarmChangeStatus')
    def test_start_schedule_range(self, AlarmChangeStatusMock: MagicMock, disable_all_schedules_mock: MagicMock):
        start_schedule_range()
        disable_all_schedules_mock.assert_called_once_with()
        AlarmChangeStatusMock.all_change_status.assert_called_once_with(True)

    @patch('alarm.use_cases.alarm_range_schedule.enable_all_schedules')
    @patch('alarm.use_cases.alarm_range_schedule.AlarmChangeStatus')
    def test_end_schedule_range(self, AlarmChangeStatusMock: MagicMock, enable_all_schedules: MagicMock):
        end_schedule_range()
        enable_all_schedules.assert_called_once_with()
        AlarmChangeStatusMock.all_change_status.assert_called_once_with(False)
