from celery import shared_task
from devices.models import Device
from mqtt_services.business.mqtt_services import is_in_status_since
from notification.tasks import send_message
from django.utils.translation import gettext as _


@shared_task()
def verify_service_status(device_id: str, service_name: str, status: bool, since_time) -> None:
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
