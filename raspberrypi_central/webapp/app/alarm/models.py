import json
import uuid

from django.utils import timezone
from django.db import models
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from alarm.business.alarm import get_next_off_schedule, get_next_on_schedule
from devices.models import Device
from house.models import House
from django.db import transaction

class AlarmStatus(models.Model):
    running = models.BooleanField()
    device = models.OneToOneField(Device, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        from alarm.communication.out_alarm import notify_alarm_status_factory
        notify_alarm_status_factory().publish_status_changed(self.device_id, self.running)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Status is {self.running} for {self.device}'


class AlarmScheduleManager(models.Manager):
    def get_next_off(self):
        return get_next_off_schedule(timezone.now(), self)

    def get_next_on(self):
        return get_next_on_schedule(timezone.now(), self)


class AlarmSchedule(models.Model):
    objects = AlarmScheduleManager()

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    start_time = models.TimeField()
    end_time = models.TimeField()

    monday    = models.BooleanField()
    tuesday   = models.BooleanField()
    wednesday = models.BooleanField()
    thursday  = models.BooleanField()
    friday    = models.BooleanField()
    saturday  = models.BooleanField()
    sunday    = models.BooleanField()

    is_disabled_by_system = models.BooleanField(default=False)

    turn_on_task = models.OneToOneField(
        PeriodicTask,
        editable=False,
        on_delete=models.PROTECT,
        related_name='alarm_schedule_on'
    )

    turn_off_task = models.OneToOneField(
        PeriodicTask,
        editable=False,
        on_delete=models.PROTECT,
        related_name='alarm_schedule_off'
    )

    alarm_statuses = models.ManyToManyField(
        AlarmStatus,
        related_name='alarm_schedules'
    )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().delete(*args, **kwargs)

            if self.turn_off_task:
                self.turn_off_task.delete()

            if self.turn_on_task:
                self.turn_on_task.delete()


    def save(self, *args, **kwargs):
        days = []

        def model_boolean_fields_to_cron_days():
            possible_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

            """
            Celery "day_of_the_week" inputs: "A (list of) integers from 0-6, where Sunday = 0 and Saturday = 6, that represent the days of a week that execution should occur."
            https://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab.day_of_week
            So we are mapping values to int.
            """
            for day_int, day_str in enumerate(possible_days, start=0):
                if getattr(self, day_str):
                    days.append(str(day_int))

            # Celery crontab want a list as str, ex: "monday,tuesday,..."
            cron_days = ','.join(days)

            return cron_days

        cron_days = model_boolean_fields_to_cron_days()

        house_timezone = House.objects.get_system_house().timezone

        if self._state.adding is True:
            self.uuid = str(uuid.uuid4())

            schedule_turn_on_alarm = CrontabSchedule.objects.create(
                minute=self.start_time.minute,
                hour=self.start_time.hour,
                day_of_week=cron_days,
                timezone=house_timezone
            )

            self.turn_on_task = PeriodicTask.objects.create(
                name=f'Turn on alarm {self.uuid}',
                task='alarm.set_alarm_on',
                crontab=schedule_turn_on_alarm,
                args=json.dumps([self.uuid])
            )

            schedule_turn_off_alarm = CrontabSchedule.objects.create(
                minute=self.end_time.minute,
                hour=self.end_time.hour,
                day_of_week=cron_days,
                timezone=house_timezone
            )

            self.turn_off_task = PeriodicTask.objects.create(
                name=f'Turn off alarm {self.uuid}',
                task='alarm.set_alarm_off',
                crontab=schedule_turn_off_alarm,
                args=json.dumps([self.uuid])
            )

        else:
            on_crontab = self.turn_on_task.crontab
            off_crontab = self.turn_off_task.crontab

            on_crontab.minute = self.start_time.minute
            on_crontab.hour = self.start_time.hour
            on_crontab.day_of_week = cron_days

            off_crontab.minute = self.end_time.minute
            off_crontab.hour = self.end_time.hour
            off_crontab.day_of_week = cron_days

            on_crontab.save()
            off_crontab.save()

        super().save(*args, **kwargs)
