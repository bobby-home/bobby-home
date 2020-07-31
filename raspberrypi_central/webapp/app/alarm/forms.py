from django import forms
from alarm.models import AlarmSchedule

class AlarmScheduleForm(forms.ModelForm):

    class Meta:
        model = AlarmSchedule
        fields = '__all__'
