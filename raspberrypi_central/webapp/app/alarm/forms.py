from django import forms
from django.forms import modelformset_factory

from alarm.models import AlarmSchedule, CameraRectangleROI, AlarmStatus, CameraROI


class AlarmScheduleForm(forms.ModelForm):

    class Meta:
        model = AlarmSchedule
        fields = '__all__'


class CameraROIForm(forms.ModelForm):
    class Meta:
        model = CameraROI
        exclude = ('define_picture',)


class CameraROIUpdateForm(forms.ModelForm):
    class Meta:
        model = CameraROI
        exclude = ('define_picture', 'device')


class CameraRectangleROIForm(forms.ModelForm):

    class Meta:
        model = CameraRectangleROI
        fields = '__all__'

CameraRectangleROIFormSet = modelformset_factory(CameraRectangleROI, exclude=('camera_roi',))

class AlarmStatusForm(forms.ModelForm):
    class Meta:
        model = AlarmStatus
        fields = '__all__'
