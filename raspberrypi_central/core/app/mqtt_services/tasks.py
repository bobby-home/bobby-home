from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from devices.models import Device
from mqtt_services.business.mqtt_services import is_in_status_since
from mqtt_services.models import MqttServicesConnectionStatusLogs
from notification.tasks import send_message
from django.utils.translation import gettext as _


@shared_task()
def verify_service_status(device_id: str, service_name: str, status: bool, since_time) -> None:
    """
    Task to verify if a service has turned `status` since a given time.
    Usage: when the system sends a mqtt message to change the status of a service and it want to check if the status of the service actually changed.
    Generally, it is used with a countdown of some seconds to let the service the time to change.
    """
    if not is_in_status_since(device_id, service_name, status, since_time):
        device = Device.objects.with_location().get(device_id=device_id)

        on_text = _('turn on')
        off_text = _('turn off')
        text = off_text
        if status:
            text = on_text

        send_message(
            _('Your service %(service)s, on the device %(device)s in %(location)s, should %(status_text)s but the system did not receive any sign of life. Something is wrong.') % {
                'service': service_name,
                'device': device.name,
                'location': device.location,
                'status_text': text }
        )


@shared_task()
def mqtt_status_does_not_match_database(device_id: str, received_status: bool, service_name: str):
    """
    Task to react when the system received a mqtt status that does not match to the database status.
    For example, in the database the alarm status is on and the system receives a mqtt message that indicates a disconnect
    from the alarm.
    That indicates a failure in the system.
    """
    device = Device.objects.with_location().get(device_id=device_id)

    turn_on = _('has turned on')
    turn_off = _('has turned off')
    off = _('off')
    on = _('on')

    turn = turn_off
    status = on

    if received_status is True:
        turn = turn_on
        status = off

    send_message(
        _('Your service %(service)s, on the device %(device)s in %(location)s, %(turn)s but it should be %(status)s. Something is wrong.') % {
            'service': service_name,
            'device': device.name,
            'location': device.location,
            'turn': turn,
            'status': status
        }
    )

@shared_task()
def cleanup() -> None:
    how_many_hour = 1
    MqttServicesConnectionStatusLogs.objects.filter(created_at__lte=timezone.now() - timedelta(hours=how_many_hour)).delete()
