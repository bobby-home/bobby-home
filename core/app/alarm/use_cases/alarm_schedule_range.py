from alarm.business.alarm_schedule_range import get_current_schedule_range
from typing import Optional
from alarm.use_cases.alarm_status import AlarmChangeStatus
import json

from django.utils import timezone
from alarm.business.alarm_schedule import disable_all_schedules, enable_all_schedules
import uuid
from alarm.models import AlarmScheduleDateRange
from django.db import transaction
from django_celery_beat.models import ClockedSchedule, PeriodicTask
import alarm.tasks as alarm_tasks


@transaction.atomic()
def create_alarm_schedule_range(schedule: AlarmScheduleDateRange) -> AlarmScheduleDateRange:
    if schedule.datetime_start <= timezone.now():
        alarm_tasks.start_schedule_range(None)
    else:
        uid = str(uuid.uuid4())
        schedule.uuid = uid

        clocked_turn_on = ClockedSchedule.objects.create(clocked_time=schedule.datetime_start)
        schedule.turn_on_task = PeriodicTask.objects.create(
            name=f'Turn on alarm for range {uid}',
            task='alarm.start_schedule_range',
            clocked=clocked_turn_on,
            one_off=True,
            args=json.dumps([uid])
        )

        if schedule.datetime_end:
            clocked_turn_off = ClockedSchedule.objects.create(clocked_time=schedule.datetime_end)
            schedule.turn_off_task = PeriodicTask.objects.create(
                name=f'Turn off alarm for range {uid}',
                task="alarm.end_schedule_range",
                clocked=clocked_turn_off,
                one_off=True,
                args=json.dumps([uid])
            )

    schedule.save()
    return schedule


@transaction.atomic()
def update_alarm_schedule_range(schedule: AlarmScheduleDateRange):
    """
    Update operation is complexe involving same tests as the creation.
    To remove this complexity, we delete the schedule and recreate one.
    """
    schedule.delete()
    return create_alarm_schedule_range(schedule)

@transaction.atomic()
def stop_current_alarm_schedule_range() -> Optional[AlarmScheduleDateRange]:
    schedule = get_current_schedule_range()
    if schedule is None:
        return None

    schedule.datetime_end = timezone.now()

    if schedule.turn_off_task:
        schedule.turn_off_task.delete()

    alarm_tasks.end_schedule_range(str(schedule.uuid))

    schedule.save()
    return schedule

def start_schedule_range():
    disable_all_schedules()
    AlarmChangeStatus.all_change_status(True)


def end_schedule_range():
    enable_all_schedules()
    AlarmChangeStatus.all_change_status(False)

