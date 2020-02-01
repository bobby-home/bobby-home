from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from enum import Enum
import uuid


class Location(models.Model):
    structure = models.CharField(max_length=60)
    sub_structure = models.CharField(max_length=60)

    def __str__(self):
        return '{0}_{1}'.format(self.structure, self.sub_structure)
    
    class Meta:
        unique_together = ['structure', 'sub_structure']


class DeviceType(models.Model):
    '''
    RaspberryPI4, zero w, zero, arduino uno, esp8266...
    '''
    type = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.type


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True, blank=True)
    location = models.ForeignKey('Location', on_delete=models.PROTECT)
    device_type = models.ForeignKey('DeviceType', on_delete=models.PROTECT)

    def __str__(self):
        return '{0}_{1}'.format(self.name, self.device_type)

class Attachment(models.Model):
    S3 = 0

    TYPE_CHOICES = [
        (S3, 'Amazon s3')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    bucket_name = models.CharField(max_length=60)
    object_name = models.CharField(max_length=100)
    storage_type = models.IntegerField(choices=TYPE_CHOICES)

    def __str__(self):
        return '{0}_{1}_{2}'.format(self.bucket_name, self.object_name, self.storage_type)



class AlertType(models.Model):
    type = models.CharField(primary_key=True, max_length=60)

    def __str__(self):
        return '{0}'.format(self.type)


class SeverityChoice(models.TextChoices):
    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'

class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    severity = models.CharField(max_length=60, choices=SeverityChoice.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    alert_type = models.ForeignKey(AlertType, on_delete=models.PROTECT)
    attachments = models.ManyToManyField(Attachment, blank=True)
    devices = models.ManyToManyField(Device, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = timezone.now()
        # else: lock the update?! Raise an error here?
        return super(Alert, self).save(*args, **kwargs)


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
