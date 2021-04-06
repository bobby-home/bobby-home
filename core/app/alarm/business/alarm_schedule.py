
DAYS_OF_WEEK = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')


def get_current_day(now):
    return DAYS_OF_WEEK[now.isoweekday() -1]


def get_next_off_schedule(now, alarm_schedule):
    current_day = get_current_day(now)

    next_schedule = alarm_schedule.filter(start_time__lte=now, end_time__gt=now, **{f'{current_day}': True}).order_by('end_time')[:1]

    if len(next_schedule) == 1:
        return next_schedule[0]

    return None


def get_next_on_schedule(now, alarm_schedule):
    current_day = get_current_day(now)

    next_schedule = alarm_schedule.filter(start_time__gt=now, end_time__gt=now, **{f'{current_day}': True}).order_by('start_time')[:1]

    if len(next_schedule) == 1:
        return next_schedule[0]

    return None

def get_device_next_off_schedule(now, device_pk: int):
    from alarm.models import AlarmSchedule

    current_day = get_current_day(now)

    next_schedule = AlarmSchedule.objects.filter(alarm_statuses__device=device_pk, start_time__lte=now, end_time__gt=now, **{f'{current_day}': True}).order_by('start_time')[:1]

    if len(next_schedule) == 1:
        return next_schedule[0]

    return None

def get_device_next_on_schedule(now, device_pk: int):
    from alarm.models import AlarmSchedule
    current_day = get_current_day(now)
    next_schedule = AlarmSchedule.objects.filter(alarm_statuses__device=device_pk, start_time__gt=now, end_time__gt=now, **{f'{current_day}': True}).order_by('start_time')[:1]

    if len(next_schedule) == 1:
        return next_schedule[0]

    return None
