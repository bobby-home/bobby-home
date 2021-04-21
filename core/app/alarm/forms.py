from django import forms
from django.db import transaction
from alarm.use_cases.alarm_status import AlarmChangeStatus
from alarm.models import AlarmSchedule, AlarmStatus


class AlarmScheduleForm(forms.ModelForm):

    class Meta:
        model = AlarmSchedule
        fields = '__all__'


class AlarmStatusForm(forms.ModelForm):
    class Meta:
        model = AlarmStatus
        fields = ['running']
    
    def save(self, commit: bool = True) -> AlarmStatus:
        instance = super().save(commit=False)
        AlarmChangeStatus().save_status(instance)
        return instance

