import uuid 
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, PeriodicTask
from django.db import models
from house.models import House
import pytz
from . import tasks


class AlarmScheduleDateRange(models.Model):
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()

    turn_on_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_date_range_on')
    turn_off_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_date_range_off')

    """
    Ex: I'm out from monday 8h to friday 17h
    -> We have to create two one tape schedules as AlarmSchedule does
    -> We have to disable active AlarmSchedule when we're starting the alarm
    -> We have to enable every AlarmSchedule that has been disabled by the system when the resident is back
    -> The user can says that is here sooner
    """
    def save(self, *args, **kwargs):
        if self._state.adding is True:
            uid = uuid.uuid4()

            schedules = AlarmSchedule.objects.filter(is_disabled_by_system=False)

            for schedule in schedules:
                schedule.disable()
            
            clocked_turn_on = ClockedSchedule.objects.create(clocked_time=self.datetime_start)
            self.turn_on_task = PeriodicTask.objects.create(
                name=f'Turn on alarm for holidays {uid}',
                task='alarm.set_alarm_on',
                clocked=clocked_turn_on,
                one_off=True
            )

            # @TODO: turn off with another task:
            # 1) off the alarm via mqtt 2) THEN delete this!
            clocked_turn_off = ClockedSchedule.objects.create(clocked_time=self.datetime_end)
            self.turn_off_task = PeriodicTask.objects.create(
                name=f'Turn off alarm for holidays {uid}',
                task='alarm.set_alarm_off',
                clocked=clocked_turn_off,
                one_off=True
            )
        else:
            on_clock = self.turn_on_task.clocked
            off_clock = self.turn_off_task.clocked

            on_clock.clocked_time = self.datetime_start
            off_clock.clocked_time = self.datetime_end

            on_clock.save()
            off_clock.save()

        super().save(*args, **kwargs)

    def delete(self):
        schedules = AlarmSchedule.objects.filter(is_disabled_by_system=True)

        for schedule in schedules:
            schedule.enable()

        super(AlarmScheduleDateRange, self).delete()

def create_celery_schedules(uid: str, timezone: str, cron_days: str, hour_start, minute_start, hour_end, minute_end):

    schedule_turn_on_alarm = CrontabSchedule.objects.create(
        minute=minute_start,
        hour=hour_start,
        day_of_week=cron_days,
        timezone=timezone
    )

    turn_on_task = PeriodicTask.objects.create(
        name=f'Turn on alarm {uid}',
        task='alarm.set_alarm_on',
        crontab=schedule_turn_on_alarm
    )

    schedule_turn_off_alarm = CrontabSchedule.objects.create(
        minute=minute_end,
        hour=hour_end,
        day_of_week=cron_days,
        timezone=timezone
    )

    turn_off_task = PeriodicTask.objects.create(
        name=f'Turn off alarm {uid}',
        task='alarm.set_alarm_off',
        crontab=schedule_turn_off_alarm
    )

    return {'turn_off_task': turn_off_task, 'turn_on_task': turn_on_task}

class AlarmSchedule(models.Model):
    hour_start = models.IntegerField()
    minute_start = models.IntegerField()

    hour_end = models.IntegerField()
    minute_end = models.IntegerField()

    monday    = models.BooleanField(default=False)
    tuesday   = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday  = models.BooleanField(default=False)
    friday    = models.BooleanField(default=False)
    saturday  = models.BooleanField(default=False)
    sunday    = models.BooleanField(default=False)

    is_disabled_by_system = models.BooleanField(default=False)

    turn_on_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_on')
    turn_off_task = models.OneToOneField(PeriodicTask, blank=True, null=True, on_delete=models.CASCADE, related_name='alarm_schedule_off')

    def disable(self, *args, **kwargs):
        self.is_disabled_by_system = True
        self.turn_on_task.enabled = False
        self.turn_off_task.enabled = False

        self.turn_on_task.save()
        self.turn_off_task.save()

        super().save(*args, **kwargs)

    def enable(self, *args, **kwargs):
        self.is_disabled_by_system = False
        self.turn_on_task.enabled = True
        self.turn_off_task.enabled = True

        self.turn_on_task.save()
        self.turn_off_task.save()

        super().save(*args, **kwargs)


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
        uid = uuid.uuid4()

        if self._state.adding is True:
            tasks = create_celery_schedules(uid, house_timezone, cron_days, self.hour_start, self.minute_start, self.hour_end, self.minute_end)
            self.turn_off_task = tasks['turn_off_task']
            self.turn_on_task = tasks['turn_on_task']
        else:
            on_crontab = self.turn_on_task.crontab
            off_crontab = self.turn_off_task.crontab

            on_crontab.minute = self.minute_start
            on_crontab.hour = self.hour_start
            on_crontab.day_of_week = cron_days

            off_crontab.minute = self.minute_end
            off_crontab.hour = self.hour_end
            off_crontab.day_of_week = cron_days

            on_crontab.save()
            off_crontab.save()

        super().save(*args, **kwargs)


class AlarmStatus(models.Model):
    running = models.BooleanField()

    # only one row can be created, otherwise: IntegrityError is raised.
    # from https://books.agiliq.com/projects/django-orm-cookbook/en/latest/singleton.html
    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        
        tasks.alarm_status_changed.delay(self.running)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Status is {self.running}'
