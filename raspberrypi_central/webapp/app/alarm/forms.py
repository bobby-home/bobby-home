from django import forms
from alarm.models import AlarmSchedule, CameraRectangleROI

class AlarmScheduleForm(forms.ModelForm):

    class Meta:
        model = AlarmSchedule
        fields = '__all__'


class CameraRectangleROIForm(forms.ModelForm):

    class Meta:
        model = CameraRectangleROI
        fields = '__all__'
