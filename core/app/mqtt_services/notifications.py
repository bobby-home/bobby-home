from devices.models import Device
from notification.tasks import send_message
from django.utils.translation import gettext as _


def service_status(service_name: str, status: bool, device: Device) -> None:
    on_text = _('turn on')
    off_text = _('turn off')
    text = off_text

    if status:
        text = on_text

    send_message(
        _(
            'Your service %(service)s, on the device %(device)s in %(location)s, should %(status_text)s but the system did not receive any sign of life. Something is wrong.') % {
            'service': service_name,
            'device': device.name,
            'location': device.location,
            'status_text': text}
    )

def mqtt_status_does_not_match_database(service_name: str, received_status: bool, device: Device) -> None:
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
