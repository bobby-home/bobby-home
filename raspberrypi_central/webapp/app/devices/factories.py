import factory
from faker import Factory

faker = Factory.create()

from .models import (
    Location,

    DeviceType,
    Device,

    AlertType,
    Alert,
)


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
    
    name = faker.name()
    device_type = factory.SubFactory(DeviceTypeFactory)
    location = factory.SubFactory(LocationFactory)


class AlertTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlertType

class AlertFactory(factory.DjangoModelFactory):
    class Meta:
        model = Alert

    alert_type = factory.SubFactory(AlertTypeFactory)

    @factory.post_generation
    def devices(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for device in extracted:
                self.devices.add(device)
