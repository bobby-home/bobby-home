from datetime import timedelta

import factory
from django.utils import timezone
from faker import Factory

from devices.factories import DeviceFactory
from .models import AlarmStatus, AlarmSchedule

faker = Factory.create()

class AlarmStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlarmStatus

    running = True
    device = factory.SubFactory(DeviceFactory)


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
