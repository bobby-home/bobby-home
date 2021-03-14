from typing import List

from django.views.generic import TemplateView

from alarm.models import AlarmStatus


class AlarmHome(TemplateView):
    template_name = "camera/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        alarms: List[AlarmStatus] = AlarmStatus.objects.select_related('device__location').order_by('device__device_id')
        context['alarms'] = alarms

        return context
