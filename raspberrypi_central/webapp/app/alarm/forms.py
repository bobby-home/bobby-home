from django import forms

from alarm.models import AlarmSchedule, AlarmStatus


class AlarmScheduleForm(forms.ModelForm):

    class Meta:
        model = AlarmSchedule
        fields = '__all__'


class AlarmStatusForm(forms.ModelForm):
    class Meta:
        model = AlarmStatus
        fields = '__all__'
