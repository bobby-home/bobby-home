from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DetailView
from django.views.generic.edit import CreateView

from alarm.business.alarm_schedule import DAYS_OF_WEEK
from alarm.models import AlarmStatus, AlarmSchedule
from utils.django.forms import ChangeForm
from utils.django.json_view import JsonableResponseMixin


class AlarmStatusCreate(CreateView):
    model = AlarmStatus
    fields = '__all__'
    template_name = 'alarm/status_form.html'


class AlarmStatusUpdate(JsonableResponseMixin, UpdateView):
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


class AlarmStatusList(ListView):
    queryset = AlarmStatus.objects.all()
    template_name = 'alarm/status_list.html'
    context_object_name = 'statuses'


class AlarmStatusSchedules(DetailView):
    model = AlarmStatus
    template_name = 'alarm/status_schedules.html'
    context_object_name = 'alarm'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # alarm_status: AlarmStatus = context[self.context_object_name]

        context['DAYS_OF_WEEK'] = DAYS_OF_WEEK

        return context

class AlarmScheduleUpdate(JsonableResponseMixin, ChangeForm, UpdateView):
    model = AlarmSchedule
    fields = '__all__'

    def get_success_url(self):
        return reverse('alarm:schedule-detail', args=(self.object.id,))

class AlarmScheduleCreate(ChangeForm, CreateView):
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
