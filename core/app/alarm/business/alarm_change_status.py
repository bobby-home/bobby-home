from typing import List

from django.db import transaction

from alarm.business.alarm_status import alarm_statuses_changed
from alarm.models import AlarmSchedule, AlarmStatus, Ping


def change_status(alarm_statuses: List[AlarmStatus], status: bool, force: bool = False) -> None:
    for alarm_status in alarm_statuses:
        alarm_status: AlarmStatus
        alarm_status.running = status

        try:
            ping = Ping.objects.get(
                device_id=alarm_status.device.device_id,
                service_name='object_detection')

            ping.failures += ping.consecutive_failures
            ping.consecutive_failures = 0
            ping.save()
        except Ping.DoesNotExist:
            pass

    AlarmStatus.objects.bulk_update(alarm_statuses, ['running'])
    transaction.on_commit(lambda: alarm_statuses_changed(alarm_statuses, force=force))


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

            change_status(alarm_statuses, status)

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

            change_status(alarm_statuses, status, force)
