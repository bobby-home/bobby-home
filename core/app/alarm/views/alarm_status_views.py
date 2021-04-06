from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DetailView, TemplateView
from django.views.generic.edit import CreateView

from alarm.business.alarm_schedule import DAYS_OF_WEEK
from alarm.business.alarm_status import alarm_status_changed
from alarm.models import AlarmStatus, AlarmSchedule
from devices.models import Device
from utils.django.forms import ChangeForm
from utils.django.json_view import JsonableResponseMixin
from utils.views import HTMLFormMessageFieldBased


class AlarmHome(LoginRequiredMixin, TemplateView):
    template_name = "alarm/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        alarms: List[AlarmStatus] = AlarmStatus.objects.select_related('device__location').order_by('device__device_id').prefetch_related('alarm_schedules')
        context['alarms'] = alarms

        return context


class AlarmStatusCreate(LoginRequiredMixin, ChangeForm, CreateView):
    model = AlarmStatus
    fields = '__all__'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Device -> Alarm is a OneToOne relationship.
        # If a device is already linked to an alarm status, don't propose it through the form.
        form.fields['device'].queryset = Device.objects.filter(alarmstatus=None)
        return form

    def form_valid(self, form):
        res = super().form_valid(form)
        alarm_status_changed(self.object)
        return res

class AlarmStatusUpdate(LoginRequiredMixin, JsonableResponseMixin, ChangeForm, UpdateView):
    model = AlarmStatus
    fields = ['running']
    template_name = 'alarm/status_form.html'
    success_url = reverse_lazy('alarm:home')

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

    def form_valid(self, form):
        res = super().form_valid(form)
        alarm_status_changed(self.object)
        return res


class AlarmStatusDetail(LoginRequiredMixin, DetailView):
    model = AlarmStatus
    template_name = 'alarm/alarm_detail.html'
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
