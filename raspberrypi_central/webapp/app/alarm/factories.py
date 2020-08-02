import factory
from faker import Factory
from factory.faker import faker
from datetime import datetime

fake = faker.Faker()

from .models import (
    AlarmSchedule
)

class AlarmScheduleFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlarmSchedule

    hour_start = factory.LazyFunction(lambda: datetime.now().hour)
    minute_start = factory.LazyFunction(lambda: datetime.now().minute)

    hour_end = factory.LazyFunction(lambda: datetime.now().hour)
    minute_end = factory.LazyFunction(lambda: datetime.now().minute)
