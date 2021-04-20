from alarm.models import Ping, AlarmStatus
from devices.models import Device
from house.models import Location
from house.utils import format_utc_datetime
from notification.consts import SeverityChoice
import notification.tasks as notification_tasks
from django.utils.translation import gettext as _


def object_detected(device: Device) -> None:
    location = device.location
    message = _('People has been detected in %(structure)s %(sub_structure)s') % {
        'structure': location.structure,
        'sub_structure': location.sub_structure,
    }

    kwargs = {
        'severity': SeverityChoice.HIGH,
        'device_id': device.device_id,
        'message': message
    }

    notification_tasks.create_and_send_notification.apply_async(kwargs=kwargs)


def object_no_more_detected(device: Device) -> None:
    location = device.location
    message = _("People detected in %(structure)s %(sub_structure)s is no longer detected.") % {
        'structure': location.structure,
        'sub_structure': location.sub_structure,
    }

    kwargs = {
        'severity': SeverityChoice.HIGH,
        'device_id': device.device_id,
        'message': message
    }

    notification_tasks.create_and_send_notification.apply_async(kwargs=kwargs)


def service_no_ping(status: AlarmStatus, ping: Ping) -> None:
    since_msg = ' ' + _('since %(since)s') % {'since': format_utc_datetime('%Y-%m-%d %H:%M:%S', ping.last_update)} if ping.last_update else ''
    msg = _('The service object_detection for the device %(device)s does not send any ping%(since)s.') % {
        'device': status.device,
        'since': since_msg
    }

    notification_tasks.create_and_send_notification(severity=SeverityChoice.HIGH, device_id=status.device.device_id, message=msg)


def service_ping_back(status: AlarmStatus) -> None:
    msg = _('The service object_detection for the device %(device_name)s was not pinging but it does now. Everything is back to normal.') % {
        'device_name': status.device
    }

    notification_tasks.create_and_send_notification(severity=SeverityChoice.HIGH, device_id=status.device.device_id, message=msg)
