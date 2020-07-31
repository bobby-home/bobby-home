from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.db import models
import pytz
from . import tasks


class AlarmSchedule(models.Model):
    hour_start = models.IntegerField()
    minute_start = models.IntegerField()

    hour_end = models.IntegerField()
    minute_end = models.IntegerField()

    monday    = models.BooleanField()
    tuesday   = models.BooleanField()
    wednesday = models.BooleanField()
    thursday  = models.BooleanField()
    friday    = models.BooleanField()
    saturday  = models.BooleanField()
    sunday    = models.BooleanField()

    turn_on_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_on')
    turn_off_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_off')


    def save(self, *args, **kwargs):
        days = []

        possible_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        """
        Celery "day_of_the_week" inputs: "A (list of) integers from 0-6, where Sunday = 0 and Saturday = 6, that represent the days of a week that execution should occur."
        https://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab.day_of_week
        So we are mapping values to int.
        """
        for day_int, day_str in enumerate(possible_days, start=0):
            if getattr(self, day_str):
                days.append(str(day_int))
    
        cron_days = ','.join(days)
        print(cron_days)
        europe_tmz = pytz.timezone('Europe/Paris')

        schedule_turn_on_alarm, _ = CrontabSchedule.objects.get_or_create(
            minute=self.minute_start,
            hour=self.hour_start,
            day_of_week=cron_days,
            # @TODO: define timezone of the HOUSE.
            timezone=europe_tmz
        )

        self.turn_on_task = PeriodicTask.objects.update_or_create(
            name=f'Turn on the alarm for schedule {self.pk}',
            task='alarm.set_alarm_on',
            defaults={'crontab': schedule_turn_on_alarm}
        )

        schedule_turn_off_alarm, _ = CrontabSchedule.objects.get_or_create(
            minute=self.minute_end,
            hour=self.hour_end,
            day_of_week=cron_days,
            # @TODO: define timezone of the HOUSE.
            timezone=europe_tmz
        )

        self.turn_off_task = PeriodicTask.objects.update_or_create(
            name=f'Turn off the alarm for schedule {self.pk}',
            crontab=schedule_turn_off_alarm,
            defaults={'crontab': schedule_turn_on_alarm}
        )

        super().save(*args, **kwargs)


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
