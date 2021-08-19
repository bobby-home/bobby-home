
from django.urls.base import reverse
from django.views.generic.detail import DetailView
from alarm.forms import AlarmRangeScheduleForm
from alarm.models import AlarmScheduleDateRange
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.django.forms import ChangeForm
from django.views.generic.edit import CreateView, UpdateView


class AlarmScheduleRangeWrite(LoginRequiredMixin, ChangeForm):
    form_class = AlarmRangeScheduleForm
    model = AlarmScheduleDateRange

    def get_success_url(self):
        return reverse('alarm:absence-detail', kwargs={'pk': self.object.pk})


class AlarmScheduleRangeCreate(AlarmScheduleRangeWrite, CreateView):
    pass


class AlarmScheduleRangeUpdate(AlarmScheduleRangeWrite, UpdateView):
    pass


class AlarmScheduleRangeDetail(LoginRequiredMixin, DetailView):
    model = AlarmScheduleDateRange
