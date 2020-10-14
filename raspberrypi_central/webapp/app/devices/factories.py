import factory
from faker import Factory
import uuid
from .models import (
    Location,

    DeviceType,
    Device,
)


faker = Factory.create()


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Location

    structure = "house"
    sub_structure = "living_room"

class DeviceTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = DeviceType


class DeviceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Device

    device_id = factory.LazyAttribute(lambda obj: uuid.uuid4().__str__().split('-')[0])
    name = factory.LazyAttribute(lambda obj: faker.name())
    device_type = factory.SubFactory(DeviceTypeFactory)
    location = factory.SubFactory(LocationFactory)
