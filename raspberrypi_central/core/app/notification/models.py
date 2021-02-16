import uuid

from django.conf import settings
from django.db import models

from devices.models import Device
from notification.consts import SeverityChoice

"""
This model is removed and might be used later.
It is not used yet because we have models like CameraMotionDetectedPicture.
But the design of this Model remains good.
"""
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


class SystemNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message = models.TextField()
    severity = models.CharField(max_length=60, choices=SeverityChoice.choices)

    devices = models.ManyToManyField(Device, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class UserFreeCarrier(models.Model):
    free_user = models.CharField(max_length=80)
    free_password = models.CharField(max_length=100)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f'Configuration for {self.user.__str__()}'


class UserTelegramBotChatId(models.Model):
    # max_length is larger than the Telegram chat_id to avoid issues if it gets larger.
    chat_id = models.CharField(max_length=60)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f'Configuration for {self.user.__str__()}'


class UserSetting(models.Model):
    # @TODO ?: validation only one of these fields can be non null.
    free_carrier = models.ForeignKey(UserFreeCarrier, on_delete=models.PROTECT, blank=True, null=True)
    telegram_chat = models.ForeignKey(UserTelegramBotChatId, on_delete=models.PROTECT, blank=True, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
