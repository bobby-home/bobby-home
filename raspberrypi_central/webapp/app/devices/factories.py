import factory
from faker import Factory
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
    
    name = factory.LazyAttribute(lambda obj: faker.name())
    device_type = factory.SubFactory(DeviceTypeFactory)
    location = factory.SubFactory(LocationFactory)
