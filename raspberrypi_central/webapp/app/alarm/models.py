from django.db import models

class AlarmStatus(models.Model):
    is_active = models.BooleanField()

    # only one row can be created, otherwise: IntegrityError is raised.
    # from https://books.agiliq.com/projects/django-orm-cookbook/en/latest/singleton.html
    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)
