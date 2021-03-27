from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from alarm.models import AlarmStatus
from house.models import House, TelegramBot
import datetime, pytz

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        running_alarms: List[AlarmStatus] = AlarmStatus.objects.select_related('device__location').filter(running=True)
        context['running_alarms'] = running_alarms

        return context

class ConfigurationView(LoginRequiredMixin, TemplateView):
    template_name = "configuration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        house = House.objects.get_system_house()
        utc_offset = datetime.datetime.now(pytz.timezone(house.timezone)).strftime('%z')

        telegram_bot = TelegramBot.objects.house_token()

        context['house'] = house
        context['utc_offset'] = utc_offset
        context['telegram_bot'] = telegram_bot

        return context
