from django.forms.widgets import DateTimeInput
from alarm.use_cases.alarm_schedule_range import create_alarm_schedule_range, update_alarm_schedule_range
from alarm.use_cases.alarm_schedule import create_alarm_schedule, update_alarm_schedule
from django import forms
from django.db import transaction
from alarm.use_cases.alarm_status import AlarmChangeStatus
from alarm.models import AlarmSchedule, AlarmScheduleDateRange, AlarmStatus


class FormInformation():
    _creating: bool

    def __init__(self, *args, **kwargs):
        self._creating = kwargs.get('instance') is None
        super().__init__(*args, **kwargs)

    @property
    def is_creating(self) -> bool:
        return self._creating


class AlarmRangeScheduleForm(FormInformation, forms.ModelForm):

    class Meta:
        model = AlarmScheduleDateRange
        fields = '__all__'
        widgets = {
            'datetime_start': DateTimeInput(
                attrs={'type': 'datetime-local'},
                format="%Y-%m-%dT%H:%M"
            ),
            'datetime_end': DateTimeInput(
                attrs={'type': 'datetime-local'},
                format="%Y-%m-%dT%H:%M"
            ),
        }

    def save(self, commit: bool = True) -> AlarmScheduleDateRange:
        instance = super().save(commit=False)

        if self.is_creating:
            self.instance = create_alarm_schedule_range(instance)
        else:
            self.instance = update_alarm_schedule_range(instance)

        return self.instance

class AlarmScheduleForm(FormInformation, forms.ModelForm):

    class Meta:
        model = AlarmSchedule
        fields = '__all__'

    def save(self, commit: bool = True) -> AlarmSchedule:
        instance = super().save(commit=False)

        if self.is_creating:
            self.instance = create_alarm_schedule(instance)
        else:
            self.instance = update_alarm_schedule(instance)

        self.save_m2m()

        return self.instance


class AlarmStatusForm(forms.ModelForm):
    class Meta:
        model = AlarmStatus
        fields = ['running']

    def save(self, commit: bool = True) -> AlarmStatus:
        instance = super().save(commit=False)
        AlarmChangeStatus().save_status(instance)
        return instance

