from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView
from alarm.models import AlarmStatus


class AlarmStatusCreate(CreateView):
    model = AlarmStatus
    fields = '__all__'
    template_name = 'alarm/status_form.html'


class AlarmStatusUpdate(UpdateView):
    model = AlarmStatus
    fields = ['running']
    template_name = 'alarm/status_form.html'
    success_url = reverse_lazy('alarm:status-list')


class AlarmStatusList(ListView):
    queryset = AlarmStatus.objects.all()
    template_name = 'alarm/status_list.html'
    context_object_name = 'statuses'
