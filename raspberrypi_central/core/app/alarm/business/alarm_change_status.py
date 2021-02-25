from typing import List

from django.db import transaction

from alarm.business.alarm_status import alarm_statuses_changed
from alarm.models import AlarmSchedule, AlarmStatus


class AlarmScheduleChangeStatus:
    """
    Class to change the status of an Alarm through a Schedule.
    """
    def __init__(self):
        pass

    @staticmethod
    def set_alarm_status(alarm_status_uui: str, status: bool) -> None:
        with transaction.atomic():
            schedule = AlarmSchedule.objects.select_for_update().only('alarm_statuses__running').get(uuid=alarm_status_uui)
            alarm_statuses: List[AlarmStatus] = schedule.alarm_statuses.select_for_update().all()

            for alarm_status in alarm_statuses:
                alarm_status: AlarmStatus
                alarm_status.running = status

            AlarmStatus.objects.bulk_update(alarm_statuses, ['running'])
            transaction.on_commit(lambda: alarm_statuses_changed(alarm_statuses))

    def turn_off(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, False)

    def turn_on(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, True)

class AlarmChangeStatus:

    @staticmethod
    def all_change_status(status: bool, force: bool = False) -> None:
        """
        When the user decide to change the status of the alarm,
        the system do it for every device (alarm status).
        """
        with transaction.atomic():
            alarm_statuses: List[AlarmStatus] = AlarmStatus.objects.select_for_update().all()

            for alarm_status in alarm_statuses:
                alarm_status: AlarmStatus
                alarm_status.running = status

            AlarmStatus.objects.bulk_update(alarm_statuses, ['running'])
            transaction.on_commit(lambda: alarm_statuses_changed(alarm_statuses, force=force))
