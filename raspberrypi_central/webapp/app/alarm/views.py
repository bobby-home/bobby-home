from django.shortcuts import render
from django.views import View

from . import tasks
from alarm.forms import AlarmScheduleForm


class AlarmShapeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'alarm/shape.html')


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
