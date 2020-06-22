import factory
from faker import Factory
from .models import (
    AlertType,
    Alert,
)


faker = Factory.create()

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
