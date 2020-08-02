from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from . import models
from house.models import House
from api_keys.factories import ApiKeysFactory
from api_keys.models import APIKey
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from datetime import datetime    
from alarm.factories import AlarmScheduleFactory

class AlarmScheduleDateRangeTestCase(TestCase):
    def setUp(self):
        self.house = House(timezone='Europe/Paris')
        self.house.save()

    def test_create_schedule(self):
        alarm_schedule = AlarmScheduleFactory()

        data = {
            'datetime_start': datetime.now(),
            'datetime_end': datetime.now(),
        }

        alarm_schedule = models.AlarmScheduleDateRange(**data)
        alarm_schedule.save()

        # periodic_tasks = PeriodicTask.objects.all()
        # self.assertEqual(periodic_tasks.count(), 2)

        to_test = {
            'start': alarm_schedule.turn_on_task,
            'end': alarm_schedule.turn_off_task
        }

        for key, value in to_test.items():
            self.assertEqual(value.clocked.clocked_time, data[f'datetime_{key}'])

        all_schedules = models.AlarmSchedule.objects.all()

        for schedule in all_schedules:
            self.assertEqual(schedule.is_disabled_by_system, True)
            self.assertEqual(schedule.turn_on_task.enabled, False)
            self.assertEqual(schedule.turn_off_task.enabled, False)

        alarm_schedule.delete()
        all_schedules = models.AlarmSchedule.objects.all()

        for schedule in all_schedules:
            self.assertEqual(schedule.is_disabled_by_system, False)
            self.assertEqual(schedule.turn_on_task.enabled, True)
            self.assertEqual(schedule.turn_off_task.enabled, True)


class AlarmScheduleModelTestCase(TestCase):
    def setUp(self):
        self.house = House(timezone='Europe/Paris')
        self.house.save()

    def test_create_schedule(self):
        data = {
            'hour_start': 14,
            'minute_start': 14,
            'hour_end': 15,
            'minute_end': 15,
            'monday': True,
            'wednesday': True,
        }

        alarm_schedule = models.AlarmSchedule(**data)
        alarm_schedule.save()

        periodic_tasks = PeriodicTask.objects.all()

        self.assertEqual(periodic_tasks.count(), 2)

        to_test = {
            'start': alarm_schedule.turn_on_task,
            'end': alarm_schedule.turn_off_task
        }

        for key, value in to_test.items():
            self.assertEqual(value.enabled, True)
            self.assertEqual(value.crontab.timezone, self.house.timezone)
            self.assertEqual(value.crontab.hour, data[f'hour_{key}'])
            self.assertEqual(value.crontab.minute, data[f'minute_{key}'])


class AlarmViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        ApiKeysFactory()
        self.key = APIKey.objects.get(pk=1)

    def test_create(self):
        print(f'key={self.key.key}')

        res1 = self.client.post(
            reverse('alarmstatus-list'),
            {'running': True},
            format="json",
            **{'HTTP_API_KEY': self.key.key})

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res1.data, {'running': True})

        self.assertEqual(models.AlarmStatus.objects.count(), 1)
        self.assertEqual(models.AlarmStatus.objects.get().running, True)

        res_get = self.client.get(reverse('alarmstatus-list'), **{'HTTP_API_KEY': self.key.key})
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        # self.assertEqual(res_get.data, {'id': 1, 'running': True})

        res2 = self.client.post(
            reverse('alarmstatus-list'),
            {'running': False},
            format="json",
             **{'HTTP_API_KEY': self.key.key})

        self.assertEqual(res2.data, {'running': False})
        self.assertEqual(models.AlarmStatus.objects.count(), 1)
        self.assertEqual(models.AlarmStatus.objects.get().running, False)
