from alarm.models import AlarmStatus
from django.utils.translation import gettext as _

OFF_ALL = _('Deactivate all')
ON_ALL = _('Activate all')
CHOOSE = _('Choose alarm')
NO_ALARM = _('No alarm configured.')
ALL_ON = _('All of your alarms are on.')
ALL_OFF = _('All of your alarms are off.')
CHOOSE_EXPLAIN = _('What do you want to do?')
WRONG = _('Something went wrong.')


def alarm_status(status: AlarmStatus) -> str:
    if status.running:
        return _('Your alarm %(alarm)s is on.') % {'alarm': status.device.location}
    
    return _('Your alarm %(alarm)s is off.') % {'alarm': status.device.location}


def change_alarm_status(status: AlarmStatus) -> str:
    if status.running:
        return _('Desactivate alarm %(device)s.') % {'device': status.device.location}
    
    return _('Activate alarm %(device)s.') % {'device': status.device.location}


def alarm_status_changed(status: AlarmStatus) -> str:
    if status.running:
        return _('Alarm %(device)s turned on.') % {'device': status.device.location}

    return _('Alarm %(device)s turned off.') % {'device': status.device.location}

