from account.models import Account

import factory
from faker import Factory
from django.contrib.auth.hashers import make_password

faker = Factory.create()

DEFAULT_PASSWORD = 'pi3.1415'

class AccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = Account

    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    password = factory.LazyFunction(lambda: make_password(DEFAULT_PASSWORD))
