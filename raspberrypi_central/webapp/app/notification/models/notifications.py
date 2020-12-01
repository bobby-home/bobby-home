import uuid

from django.db import models

from devices.models import Device

# class Attachment(models.Model):
#     S3 = 0
#
#     TYPE_CHOICES = [
#         (S3, 'Amazon s3')
#     ]
#
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#
#     bucket_name = models.CharField(max_length=60)
#     object_name = models.CharField(max_length=100)
#     storage_type = models.IntegerField(choices=TYPE_CHOICES)
#
#     def __str__(self):
#         return '{0}_{1}_{2}'.format(self.bucket_name, self.object_name, self.storage_type)

class SeverityChoice(models.TextChoices):
    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'


class SystemNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message = models.TextField()
    severity = models.CharField(max_length=60, choices=SeverityChoice.choices)

    # attachments = models.ManyToManyField(Attachment, blank=True)
    devices = models.ManyToManyField(Device, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
