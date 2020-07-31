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
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})

class AlarmStatusViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasAPIAccess,)

    queryset = models.AlarmStatus.objects.all()
    serializer_class = serializers.AlarmStatusSerializer

    def create(self, request):
        serializer = serializers.AlarmStatusSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        request_status = request.data.get('running')

        if (request_status == True):
            models.AlarmStatus.objects.update_or_create(pk=1, defaults={'running': True})
        elif (request_status == False):
            models.AlarmStatus.objects.update_or_create(pk=1, defaults={'running': False})

        return Response(serializer.data, status=status.HTTP_201_CREATED)
