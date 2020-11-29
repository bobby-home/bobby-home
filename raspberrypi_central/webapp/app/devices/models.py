from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from enum import Enum
from house.models import Location


class SeverityChoice(models.TextChoices):
    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'


class DeviceType(models.Model):
    """
    RaspberryPI4, zero w, zero, arduino uno, esp8266...
    """
    type = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.type


class Device(models.Model):
    device_id = models.CharField(max_length=8, unique=True)

    name = models.CharField(max_length=100, unique=True, blank=True)

    # When we're installing the system, location may not be known at the begining.
    location = models.ForeignKey(Location, blank=True, on_delete=models.PROTECT)
    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT)

    def __str__(self):
        return '{0}_{1}_{2}'.format(self.name, self.device_type, self.device_id)


# class SensorInformation(models.Model):
#     TEMPERATURE = 0
#     LIGHT = 1
#     MOTION = 2
#     ULTRA_SONIC = 3

#     TYPE_CHOICES = [
#         (TEMPERATURE, 'temperature'),
#         (LIGHT, 'light'),
#         (MOTION, 'motion'),
#         (ULTRA_SONIC, 'ultra sonic')
#     ]

#     type = models.IntegerField(choices=TYPE_CHOICES)
#     reference = models.CharField(max_length=100)


# class Sensor(models.Model):
#     sensor_information = models.ForeignKey('SensorInformation', on_delete=models.PROTECT)
#     device = models.ForeignKey('Device', on_delete=models.PROTECT)


# class SensorData(models.Model):
#     received_at = models.DateTimeField(editable=False)
#     # JSONField uses jsonb pgsql data type.
#     data = JSONField()
#     sensor = models.ForeignKey('Sensor', on_delete=models.PROTECT)

#     # from https://stackoverflow.com/a/1737078
#     def save(self, *args, **kwargs):
#         ''' On save, update timestamps '''
#         if not self.id:
#             self.received_at = timezone.now()
#         # else: lock the update?! Raise an error here?
#         return super(SensorData, self).save(*args, **kwargs)


# class UserCommunication(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#     )
#     data = JSONField()


# class AlertNotificationSetting(models.Model):
#     alert_type = models.ForeignKey(AlertType, on_delete=models.PROTECT)
#     severity = models.IntegerField(choices=[(tag, tag.value) for tag in SeverityChoice])

#     communication = models.ForeignKey(
#         UserCommunication,
#         on_delete=models.CASCADE,
#     )
