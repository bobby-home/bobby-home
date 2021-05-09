import uuid
import json
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.db import transaction
from alarm.models import AlarmSchedule
from house.models import House


def model_boolean_fields_to_cron_days(schedule: AlarmSchedule) -> str:
    days = []
    possible_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    """
    Celery "day_of_the_week" inputs: "A (list of) integers from 0-6, where Sunday = 0 and Saturday = 6, that represent the days of a week that execution should occur."
    https://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab.day_of_week
    So we are mapping values to int.
    """
    for day_int, day_str in enumerate(possible_days, start=0):
        if getattr(schedule, day_str):
            days.append(str(day_int))

    # Celery crontab want a list as str, ex: "monday,tuesday,..."
    cron_days = ','.join(days)
    return cron_days


@transaction.atomic
def create_alarm_schedule(schedule: AlarmSchedule):
    cron_days = model_boolean_fields_to_cron_days(schedule)
    house_timezone = House.objects.get_system_house().timezone

    schedule.uuid = str(uuid.uuid4())

    schedule_turn_on_alarm = CrontabSchedule.objects.create(
        minute=schedule.start_time.minute,
        hour=schedule.start_time.hour,
        day_of_week=cron_days,
        timezone=house_timezone
    )

    schedule.turn_on_task = PeriodicTask.objects.create(
        name=f'Turn on alarm {schedule.uuid}',
        task='alarm.set_alarm_on',
        crontab=schedule_turn_on_alarm,
        args=json.dumps([schedule.uuid])
    )

    schedule_turn_off_alarm = CrontabSchedule.objects.create(
        minute=schedule.end_time.minute,
        hour=schedule.end_time.hour,
        day_of_week=cron_days,
        timezone=house_timezone
    )

    schedule.turn_off_task = PeriodicTask.objects.create(
        name=f'Turn off alarm {schedule.uuid}',
        task='alarm.set_alarm_off',
        crontab=schedule_turn_off_alarm,
        args=json.dumps([schedule.uuid])
    )

    schedule.save()
    return schedule

@transaction.atomic
def update_alarm_schedule(schedule: AlarmSchedule):
    cron_days = model_boolean_fields_to_cron_days(schedule)

    on_crontab = schedule.turn_on_task.crontab
    off_crontab = schedule.turn_off_task.crontab

    on_crontab.minute = schedule.start_time.minute
    on_crontab.hour = schedule.start_time.hour
    on_crontab.day_of_week = cron_days

    off_crontab.minute = schedule.end_time.minute
    off_crontab.hour = schedule.end_time.hour
    off_crontab.day_of_week = cron_days

    on_crontab.save()
    off_crontab.save()
    schedule.save()

    return schedule
