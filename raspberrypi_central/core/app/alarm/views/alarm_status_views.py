from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DetailView, TemplateView
from django.views.generic.edit import CreateView

from alarm.business.alarm_schedule import DAYS_OF_WEEK
from alarm.models import AlarmStatus, AlarmSchedule
from utils.django.forms import ChangeForm
from utils.django.json_view import JsonableResponseMixin


class AlarmHome(LoginRequiredMixin, TemplateView):
    template_name = "alarm/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        alarms: List[AlarmStatus] = AlarmStatus.objects.select_related('device__location').order_by('device__device_id').prefetch_related('alarm_schedules')
        context['alarms'] = alarms

        return context


class AlarmStatusCreate(LoginRequiredMixin, CreateView):
    model = AlarmStatus
    fields = '__all__'
    template_name = 'alarm/status_form.html'


class AlarmStatusUpdate(LoginRequiredMixin, JsonableResponseMixin, UpdateView):
    model = AlarmStatus
    fields = ['running']
    template_name = 'alarm/status_form.html'
    success_url = reverse_lazy('alarm:status-list')

    context_object_name = 'alarm'
    queryset = AlarmStatus.objects.with_device_and_location()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        return context


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
