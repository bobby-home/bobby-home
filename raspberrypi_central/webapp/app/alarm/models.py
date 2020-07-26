from django.db import models
from . import tasks


class AlarmStatus(models.Model):
    running = models.BooleanField()

    # only one row can be created, otherwise: IntegrityError is raised.
    # from https://books.agiliq.com/projects/django-orm-cookbook/en/latest/singleton.html
    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        
        tasks.alarm_messaging.delay(self.running)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Status is {self.running}'
