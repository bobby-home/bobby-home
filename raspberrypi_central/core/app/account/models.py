from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings

def raise_value_error_if_not(val_name, val, msg = 'The given {} must be set'):
    if not val:
        raise ValueError(msg.format(val_name))


class MyAccountManager(BaseUserManager):
    # param: USERNAME_FIELD + REQUIRED_FIELDS
    def _create_user(self, email, first_name, last_name, password, **extra_fields):
        raise_value_error_if_not("email", email)
        raise_value_error_if_not("first_name", first_name)
        raise_value_error_if_not("last_name", last_name)

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, first_name, last_name, password, **extra_fields)


    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, first_name, last_name, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)

    """
    Required fields from Django.
    """
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    """
    Login with this field:
    """
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

