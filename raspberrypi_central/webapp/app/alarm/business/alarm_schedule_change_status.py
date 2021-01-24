from typing import List

from django.db import transaction
from alarm.models import AlarmSchedule, AlarmStatus


class AlarmScheduleChangeStatus:
    def __init__(self):
        pass

    def set_alarm_status(self, alarm_status_uui: str, status: bool) -> None:
        schedule = AlarmSchedule.objects.select_for_update().only('alarm_statuses__running').get(uuid=alarm_status_uui)
        alarm_statuses: List[AlarmStatus] = schedule.alarm_statuses.select_for_update().all()

        """
        We don't do bulk update because we have a side effect on the method `AlarmStatus.save`.
        (mqtt publish behind the scenes).
        Django does not call .save() on every modified instances (with bulk), so the side effect would not be called.
        see issues #119
        """
        with transaction.atomic():
            for alarm_status in alarm_statuses:
                alarm_status.running = status
                alarm_status.save()

    def turn_off(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, False)

    def turn_on(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, True)
