from alarm.models import AlarmStatus
from django.utils.translation import gettext as _

OFF_ALL = _('Turn off all')
ON_ALL = _('Turn on all')
CHOOSE = _('Manage alarm')
NO_ALARM = _('No alarm configured.')
ALL_ON = _('All of your alarms are on.')
ALL_OFF = _('All of your alarms are off.')
CHOOSE_EXPLAIN = _('What do you want to do?')
WRONG = _('Something went wrong.')


def alarm_status(status: AlarmStatus) -> str:
    data = {
        'location': status.device.location,
        'device': status.device.name
    }

    if status.running:
        return _('Your alarm at %(location)s on device %(device)s is on.') % data
    
    return _('Your alarm at %(location)s on device %(device)s is off.') % data


def change_alarm_status(status: AlarmStatus) -> str:
    data = {
        'location': status.device.location,
        'device': status.device.name,
    }

    if status.running:
        return _('Turn off %(location)s / %(device)s.') % data 
    
    return _('Turn on %(location)s / %(device)s.') % data


def alarm_status_changed(status: AlarmStatus) -> str:
    data = {
        'location': status.device.location,
        'device': status.device.name,
    }

    if status.running:
        return _('Your alarm at %(location)s on device %(device)s turned on.') % data 

    return _('Your alarm at %(location)s on device %(device)s turned off.') % data 

