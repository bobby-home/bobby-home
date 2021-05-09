from alarm.forms import AlarmScheduleForm
from datetime import time
from itertools import count
from unittest.case import skip
from unittest.mock import call, patch
from freezegun import freeze_time
from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from celery.schedules import schedule, crontab

from alarm.use_cases.alarm_schedule import create_alarm_schedule, model_boolean_fields_to_cron_days, update_alarm_schedule
from alarm.use_cases.alarm_status import alarm_statuses_changed
from alarm.business.alarm_schedule import get_current_day
from alarm.factories import AlarmScheduleFactory, AlarmStatusFactory
from alarm.models import AlarmSchedule
from house.factories import HouseFactory
from account.factories import AccountFactory


class AlarmScheduleToCrondays(TestCase):

    def create_model_schedule(self):
        schedule = AlarmSchedule(
            start_time=time(hour=6, minute=10),
            end_time=time(hour=8, minute=30),
            monday=True,
            tuesday=False,
            wednesday=True,
            thursday=False,
            friday=True,
            saturday=False,
            sunday=True,
        )

        return schedule

    def test_cron_day_of_week(self):
        schedule = self.create_model_schedule()
        cron_days = model_boolean_fields_to_cron_days(schedule)

        self.assertEqual('0,1,3,5', cron_days)

class ViewAlarmScheduleTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = AccountFactory()
        self.alarm_statuses = [
            AlarmStatusFactory(),
            AlarmStatusFactory(),
        ]
        self.house = HouseFactory()

        self.client.force_login(self.user)


    def test_create(self):
        
        data = {
            'sunday': True,
            'alarm_statuses': [self.alarm_statuses[0].pk],
            'start_time': '06:05',
            'end_time': '09:42'
        }

        response = self.client.post(reverse('alarm:schedule-add'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        schedules = AlarmSchedule.objects.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]

        expected_redirect = (reverse('alarm:schedule-detail', args=[schedule.pk]), HTTPStatus.FOUND)
        self.assertEqual(response.redirect_chain, [expected_redirect])

    def test_update(self):
        schedule = AlarmScheduleFactory()

        data = {
            'sunday': True,
            'alarm_statuses': [self.alarm_statuses[0].pk, self.alarm_statuses[1].pk],
            'start_time': '06:05',
            'end_time': '09:42'
        }


        response = self.client.post(reverse('alarm:schedule-edit', args=[schedule.pk]), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        expected_redirect = (reverse('alarm:schedule-detail', args=[schedule.pk]), HTTPStatus.FOUND)
        self.assertEqual(response.redirect_chain, [expected_redirect])


class FormAlarmSheculeTestCase(TestCase):
    def setUp(self) -> None:
        self.alarm_statuses = [
            AlarmStatusFactory(),
            AlarmStatusFactory(),
        ]
        self.house = HouseFactory()

    def test_create_m2m_alarm_status(self):
        form_data = {
            'sunday': True,
            'alarm_statuses': [self.alarm_statuses[0].pk],
            'start_time': '06:05',
            'end_time': '09:42'
        }

        form = AlarmScheduleForm(data=form_data)
        form.save()
        self.assertEqual(form.errors, {})

        schedules = AlarmSchedule.objects.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0] 
        
        statuses = schedule.alarm_statuses.all()
        self.assertEqual(statuses[0], self.alarm_statuses[0])

    def test_update_m2m_alarm_status(self):
        schedule = AlarmScheduleFactory()

        form_data = {
            'sunday': True,
            'alarm_statuses': [self.alarm_statuses[0].pk, self.alarm_statuses[1].pk],
            'start_time': '06:05',
            'end_time': '09:42'
        }

        form = AlarmScheduleForm(data=form_data, instance=schedule)
        form.save()
        self.assertEqual(form.errors, {})

        schedules = AlarmSchedule.objects.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0] 
        
        statuses = schedule.alarm_statuses.all()
        self.assertEqual(len(statuses), 2)
        
        self.assertEqual(statuses[0], self.alarm_statuses[0])
        self.assertEqual(statuses[1], self.alarm_statuses[1])


    @patch('alarm.forms.create_alarm_schedule')
    @patch('alarm.forms.update_alarm_schedule')
    def test_call_create_use_case(self, update_alarm_schedule_mock, create_alarm_schedule_mock):
        form_data = {
            'sunday': True,
            'alarm_statuses': [self.alarm_statuses[0].pk],
            'start_time': '06:05',
            'end_time': '09:42'
        }

        form = AlarmScheduleForm(data=form_data)
        instance = form.instance
        form.save()
        self.assertEqual(form.errors, {})
        
        create_alarm_schedule_mock.assert_called_once_with(instance)
        update_alarm_schedule_mock.assert_not_called()
    
    @patch('alarm.forms.create_alarm_schedule')
    @patch('alarm.forms.update_alarm_schedule') 
    def test_call_update_use_case(self, update_alarm_schedule_mock, create_alarm_schedule_mock):
        form_data = {
            'sunday': True,
            'alarm_statuses': [self.alarm_statuses[0].pk],
            'start_time': '06:05',
            'end_time': '09:42'
        }

        schedule = AlarmScheduleFactory()
        form = AlarmScheduleForm(data=form_data, instance=schedule)
        self.assertEqual(form.errors, {})
        instance = form.instance
        form.save()

        update_alarm_schedule_mock.assert_called_once_with(instance)
        create_alarm_schedule_mock.assert_not_called()


class UseCaseAlarmScheduleTestCase(TestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()
        self.ids = count(0)

        self.alarm_statuses = [
            AlarmStatusFactory(),
        ]

    def create_model_schedule(self):
        schedule = AlarmSchedule(
            start_time=time(hour=6, minute=10),
            end_time=time(hour=8, minute=30),
            monday=True,
            tuesday=False,
            wednesday=True,
            thursday=False,
            friday=True,
            saturday=False,
            sunday=True,
        )

        return schedule


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

        turn_on_cron = CrontabSchedule.objects.get(hour=schedule.start_time.hour, minute=schedule.start_time.minute)
        turn_off_cron = CrontabSchedule.objects.get(hour=schedule.end_time.hour, minute=schedule.end_time.minute)

        self.assertEqual(turn_off_task.crontab, turn_off_cron)
        self.assertEqual(turn_on_task.crontab, turn_on_cron)

    def test_create_alarm_schedule(self):
        schedule = self.create_model_schedule()
        #schedule.alarm_statuses.set(self.alarm_statuses)

        create_alarm_schedule(schedule)
        self._check_underlying_objects()

    def test_update_alarm_schedule(self):
        schedule = self.create_model_schedule()
        create_alarm_schedule(schedule)
 
        schedule.start_time = time(hour=4, minute=15)
        schedule.end_time = time(hour=9,minute=30)

        update_alarm_schedule(schedule)
        
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

