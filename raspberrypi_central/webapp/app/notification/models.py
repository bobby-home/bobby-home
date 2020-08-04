from django.conf import settings
from django.db import models


class FreeOperatorUserNotification(models.Model):
    free_user = models.CharField(max_length=80)
    free_password = models.CharField(max_length=100)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f'Configuration for {self.user.__str__()}'
