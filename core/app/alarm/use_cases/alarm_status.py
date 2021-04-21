from alarm.business.alarm_ping import reset_pings
from typing import List

from django.db import transaction
from alarm.use_cases.out_alarm import notify_alarm_status_factory
from alarm.models import AlarmStatus, AlarmSchedule, Ping


def alarm_status_changed(alarm_status: AlarmStatus, force=False):
    """
    Call this method when you changed an instance of alarm status.
    Used to communicate with services, to sync status.

    Parameters
    ----------
    alarm_status : AlarmStatus
        The instance that has been modified.
    force : bool
        If it's true, it forces the synchronization.
    """
    notify_alarm_status_factory().publish_status_changed(alarm_status.device_id, alarm_status, force)


def alarm_statuses_changed(alarm_statuses: List[AlarmStatus], force=False):
    """
    Call this method when you changed a list of alarm status.
    Used to communicate with services, to sync status.

    Parameters
    ----------
    alarm_statuses : List[AlarmStatus]
    force : bool
        If it's true, it forces the synchronization.
    """
    for alarm_status in alarm_statuses:
        alarm_status_changed(alarm_status, force)

def _reset_ping(alarm_statuses: List[AlarmStatus]):
    device_ids = [alarm_status.device.device_id for alarm_status in alarm_statuses]
    reset_pings(device_ids, 'object_detection')

def change_status(alarm_statuses: List[AlarmStatus], status: bool, force: bool = False) -> None:
    _reset_ping(alarm_statuses)
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

            for alarm_status in alarm_statuses:
                alarm_status.running = status

            AlarmStatus.objects.bulk_update(alarm_statuses, ['running'])
            change_status(alarm_statuses, status, force)

    @staticmethod
    def save_status(alarm_status: AlarmStatus) -> AlarmStatus:
        with transaction.atomic():
            # save + ping + change_update
            alarm_status.save()
            change_status([alarm_status], alarm_status.running, force=False)

            return alarm_status

    @staticmethod
    def reverse_status(alarm_status_pk: int, force: bool = False) -> AlarmStatus:
        with transaction.atomic():
            db_status = AlarmStatus.objects.select_for_update().get(pk=alarm_status_pk)
            status = not db_status.running

            db_status.running = status 
            db_status.save()
			
            change_status([db_status], status, force)
            return db_status

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
                alarm_status.running = status

            AlarmStatus.objects.bulk_update(alarm_statuses, ['running'])

            change_status(alarm_statuses, status)

    def turn_off(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, False)

    def turn_on(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, True)
