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

    structure = factory.Sequence(lambda n: "structure_%d" % n)
    sub_structure = factory.Sequence(lambda n: "sub_structure_%d" % n)


class DeviceTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = DeviceType

    type = factory.Sequence(lambda n: "device_type_%d" % n)


class DeviceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Device

    device_id = factory.LazyAttribute(lambda obj: uuid.uuid4().__str__().split('-')[0])
    name = factory.LazyAttribute(lambda obj: faker.name())
    device_type = factory.SubFactory(DeviceTypeFactory)
    location = factory.SubFactory(LocationFactory)
