from alarm.models import AlarmStatus
from django.utils.translation import gettext as _


# Alarm status
OFF_ALL = _('Turn off all')
ON_ALL = _('Turn on all')
CHOOSE = _('Manage alarm')
NO_ALARM = _('No alarm configured.')
ALL_ON = _('All of your alarms are on.')
ALL_OFF = _('All of your alarms are off.')
CHOOSE_EXPLAIN = _('What do you want to do?')
WRONG = _('Something went wrong.')
CANCEL = _('Cancel')
OK_CANCEL = _("Ok, I don't do anything.")

# Alarm schedule range
ABSENT_MODE = _('Absent mode.')
EXPLAIN_ABSENT_MODE = _("If you are leaving home, you can activate absent mode. It will turn on all your alarms and disable your schedules.")
OK_ABSENT_MODE = _("Ok, all your alarm is running and won't be interrupted by schedules.")

REMOVE_ABSENT_MODE = _('Remove absent mode.')
EXPLAIN_REMOVE_ABSENT_MODE = _("If you are back home, you can deactivate absent mode. It will turn off all your alarms and get your schedules back.")
OK_REMOVE_ABSENT_MODE = _("Ok, all your alarms is off and your schedules are back. Welcome home!")
KO_REMOVE_ABSENT_MODE = _("Bobby is not in absent mode so I cannot remmove this mode.")

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
