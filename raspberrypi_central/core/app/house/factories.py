
import factory
from faker import Factory

from house.models import House

faker = Factory.create()

class HouseFactory(factory.DjangoModelFactory):
    class Meta:
        model = House

    timezone = 'Europe/Tallinn'
