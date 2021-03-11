from typing import List

from django.views.generic import TemplateView

from alarm.models import AlarmStatus


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        running_alarms: List[AlarmStatus] = AlarmStatus.objects.select_related('device__location').filter(running=True)
        context['running_alarms'] = running_alarms

        return context
