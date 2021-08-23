from typing import List, Sequence
import logging
from django.db import transaction
from alarm.business.alarm_ping import reset_pings
from alarm.integration.alarm_status import integration_alarm_status_changed
from alarm.business.alarm_status import can_turn_off
from alarm.models import AlarmStatus, AlarmSchedule


LOGGER = logging.getLogger(__name__)


def alarm_statuses_changed(alarm_statuses: Sequence[AlarmStatus], force=False):
    """
    Call this method when you changed a list of alarm status.
    Used to communicate with services, to sync status.

    Parameters
    ----------
    alarm_statuses : List[AlarmStatus]
        List of instances that has been modified.
    force : bool
        If it's true, it forces the synchronization.
    """
    for alarm_status in alarm_statuses:
        if alarm_status.running is False and can_turn_off(alarm_status.device) is False and force is False:
            LOGGER.info(f'The alarm on device {alarm_status.device.device_id} should turn off but stay on because a motion is being detected. Same for services listening this event.')
            return

        integration_alarm_status_changed(alarm_status)


def _reset_ping(alarm_statuses: List[AlarmStatus]):
    device_ids = [alarm_status.device.device_id for alarm_status in alarm_statuses]
    reset_pings(device_ids, 'object_detection')


def change_statuses(alarm_statuses: List[AlarmStatus], force: bool = False) -> None:
    _reset_ping(alarm_statuses)
    transaction.on_commit(lambda: alarm_statuses_changed(alarm_statuses, force=force))


class AlarmChangeStatus:

    @staticmethod
    def all_change_statuses(status: bool, force: bool = False) -> None:
        """
        When the user decide to change the status of the alarm,
        the system do it for every device (alarm status).
        """
        with transaction.atomic():
            alarm_statuses: List[AlarmStatus] = AlarmStatus.objects.select_for_update().all()

            for alarm_status in alarm_statuses:
                alarm_status.running = status

            AlarmStatus.objects.bulk_update(alarm_statuses, ['running'])
            change_statuses(alarm_statuses, force)

    @staticmethod
    def save_status(alarm_status: AlarmStatus, force: bool = False) -> AlarmStatus:
        with transaction.atomic():
            alarm_status.save()
            change_statuses([alarm_status], force)

            return alarm_status

    @staticmethod
    def reverse_status(alarm_status_pk: int, force: bool = False) -> AlarmStatus:
        with transaction.atomic():
            db_status = AlarmStatus.objects.select_for_update().get(pk=alarm_status_pk)
            status = not db_status.running

            db_status.running = status
            db_status.save()

            change_statuses([db_status], force)
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

            change_statuses(alarm_statuses, status)

    def turn_off(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, False)

    def turn_on(self, alarm_status_uui: str) -> None:
        self.set_alarm_status(alarm_status_uui, True)
