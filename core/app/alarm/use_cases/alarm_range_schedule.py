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
def create_alarm_range_schedule(schedule: AlarmScheduleDateRange):
    print(schedule.datetime_start)
    print('---')
    print(timezone.now())

    if schedule.datetime_start <= timezone.now():
        print('past! trigger right now!')
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
def update_alarm_range_schedule(schedule: AlarmScheduleDateRange):
    on_clock = schedule.turn_on_task.clocked
    off_clock = schedule.turn_off_task.clocked

    on_clock.clocked_time = schedule.datetime_start
    off_clock.clocked_time = schedule.datetime_end

    on_clock.save()
    off_clock.save()


def start_schedule_range():
    disable_all_schedules()
    AlarmChangeStatus.all_change_status(True)


def end_schedule_range():
    enable_all_schedules()
    AlarmChangeStatus.all_change_status(False)

