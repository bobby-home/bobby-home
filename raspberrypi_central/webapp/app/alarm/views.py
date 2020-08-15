from django.shortcuts import render
from django.views import View

from api_keys.permissions import HasAPIAccess
from rest_framework import viewsets, generics, mixins, status
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from . import models
from . import tasks
from alarm.forms import AlarmScheduleForm

class AlarmView(View):
    form_class = AlarmScheduleForm
    template_name = 'alarm/schedule.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            new_schedule = form.save()
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})
