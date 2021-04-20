from typing import List

from django.db import transaction

from alarm.use_cases.alarm_status import alarm_statuses_changed
from alarm.models import AlarmSchedule, AlarmStatus, Ping


def change_status(alarm_statuses: List[AlarmStatus], status: bool, force: bool = False) -> None:
    for alarm_status in alarm_statuses:
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
