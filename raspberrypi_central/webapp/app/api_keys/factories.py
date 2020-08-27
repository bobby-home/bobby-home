import factory
from faker import Factory

from .models import APIKey

faker = Factory.create()

class ApiKeysFactory(factory.DjangoModelFactory):
    class Meta:
        model = APIKey
