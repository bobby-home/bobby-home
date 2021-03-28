from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DetailView
from django.views.generic.edit import CreateView

from alarm.business.alarm_schedule import DAYS_OF_WEEK
from alarm.models import AlarmStatus, AlarmSchedule
from devices.models import Device
from utils.django.forms import ChangeForm
from utils.django.json_view import JsonableResponseMixin
from utils.views import HTMLFormMessageFieldBased


class AlarmStatusCreate(LoginRequiredMixin, ChangeForm, CreateView):
    model = AlarmStatus
    fields = '__all__'
    # template_name = 'alarm/status_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Device -> Alarm is a OneToOne relationship.
        # If a device is already linked to an alarm status, don't propose it through the form.
        form.fields['device'].queryset = Device.objects.filter(alarmstatus=None)
        return form


class AlarmStatusUpdate(LoginRequiredMixin, JsonableResponseMixin, ChangeForm, UpdateView):
    model = AlarmStatus
    fields = ['running']
    template_name = 'alarm/status_form.html'
    success_url = reverse_lazy('alarm:status-list')

    context_object_name = 'alarm'
    queryset = AlarmStatus.objects.with_device_and_location()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        formOptions = HTMLFormMessageFieldBased(
            trueSuccess='Your alarm is now on.',
            falseSuccess='Your alarm is now off.',
            statusField='running',
            isCustomForm=True
        )

        context['formOptions'] = formOptions

        return context


class AlarmStatusList(LoginRequiredMixin, ListView):
    queryset = AlarmStatus.objects.all()
    template_name = 'alarm/status_list.html'
    context_object_name = 'statuses'


class AlarmStatusSchedules(LoginRequiredMixin, DetailView):
    model = AlarmStatus
    template_name = 'alarm/status_schedules.html'
    context_object_name = 'alarm'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # alarm_status: AlarmStatus = context[self.context_object_name]

        context['DAYS_OF_WEEK'] = DAYS_OF_WEEK

        return context

class AlarmScheduleUpdate(LoginRequiredMixin, JsonableResponseMixin, ChangeForm, UpdateView):
    model = AlarmSchedule
    fields = '__all__'

    def get_success_url(self):
        return reverse('alarm:schedule-detail', args=(self.object.id,))

class AlarmScheduleCreate(LoginRequiredMixin, ChangeForm, CreateView):
    model = AlarmSchedule
    fields = '__all__'

class AlarmScheduleDetail(DetailView):
    model = AlarmSchedule
    context_object_name = 'schedule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # alarm_status: AlarmStatus = context[self.context_object_name]

        context['DAYS_OF_WEEK'] = DAYS_OF_WEEK

        return context
