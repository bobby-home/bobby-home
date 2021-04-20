from typing import List

from alarm.use_cases.out_alarm import notify_alarm_status_factory
from alarm.models import AlarmStatus


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


