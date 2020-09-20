from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect
from . import tasks
from alarm.forms import AlarmScheduleForm, CameraRectangleROIForm

class AlarmShapeView(View):
    form_class = CameraRectangleROIForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'alarm/shape.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin/')
        else:
            return render(request, 'alarm/shape.html', {'form': form})


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
