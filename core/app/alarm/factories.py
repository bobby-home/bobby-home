from datetime import timedelta
from itertools import count
from celery.schedules import crontab
from django_celery_beat.models import CrontabSchedule, PeriodicTask

import factory
from django.utils import timezone
from faker import Factory

from devices.factories import DeviceFactory
from .models import AlarmStatus, AlarmSchedule, HTTPAlarmStatus

faker = Factory.create()


class AlarmStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlarmStatus

    running = True
    device = factory.SubFactory(DeviceFactory)


class HTTPAlarmStatusFactory(AlarmStatusFactory, factory.DjangoModelFactory):
    class Meta:
        model = HTTPAlarmStatus

    user = factory.Faker('user_name')
    password = factory.Faker('password')
    endpoint = "http://060669816:8080/cgi-bin/snap.cgi"


_ids = count(0)


def _task():
    schedule = crontab(minute='*/10')
    c = CrontabSchedule.from_schedule(schedule)
    c.save()
    return PeriodicTask.objects.create(name='t{0}'.format(next(_ids)), crontab=c)


class AlarmScheduleFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlarmSchedule

    start_time = factory.LazyFunction(timezone.now)
    end_time = factory.LazyAttribute(lambda _: timezone.now() + timedelta(hours=9))

    monday    = factory.Faker('pybool')
    tuesday   = factory.Faker('pybool')
    wednesday = factory.Faker('pybool')
    thursday  = factory.Faker('pybool')
    friday    = factory.Faker('pybool')
    saturday  = factory.Faker('pybool')
    sunday    = factory.Faker('pybool')

    turn_on_task = factory.LazyFunction(_task)
    turn_off_task = factory.LazyFunction(_task)
