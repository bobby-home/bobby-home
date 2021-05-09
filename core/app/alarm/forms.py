from alarm.use_cases.alarm_schedule import create_alarm_schedule, update_alarm_schedule
from django import forms
from django.db import transaction
from alarm.use_cases.alarm_status import AlarmChangeStatus
from alarm.models import AlarmSchedule, AlarmStatus


class AlarmScheduleForm(forms.ModelForm):
    _creating: bool

    class Meta:
        model = AlarmSchedule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self._creating = kwargs.get('instance') is None
        super().__init__(*args, **kwargs)

    def save(self, commit: bool = True) -> AlarmSchedule:
        instance = super().save(commit=False)

        if self._creating:
            create_alarm_schedule(instance)
        else:
            update_alarm_schedule(instance)

        return instance


class AlarmStatusForm(forms.ModelForm):
    class Meta:
        model = AlarmStatus
        fields = ['running']
    
    def save(self, commit: bool = True) -> AlarmStatus:
        instance = super().save(commit=False)
        AlarmChangeStatus().save_status(instance)
        return instance

