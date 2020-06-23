from django.shortcuts import render
from api_keys.permissions import HasAPIAccess
from rest_framework import viewsets, generics, mixins, status
from rest_framework.response import Response
from . import serializers
from . import models

from django.shortcuts import render


def index(request):
    status = models.AlarmStatus.objects.all()

    context = {'status': status}
    return render(request, 'home.html', context)

class AlarmStatusViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasAPIAccess,)

    queryset = models.AlarmStatus.objects.all()
    serializer_class = serializers.AlarmStatusSerializer

    def create(self, request):
        serializer = serializers.AlarmStatusSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        status = request.data.get('status')
        if (status == 'on'):
            models.AlarmStatus.objects.update_or_create(is_active=True)
        elif (status == 'off'):
            models.AlarmStatus.objects.update_or_create(is_active=False)

        return Response('WIP!')

    def list(self, request):
        alarm_status = models.AlarmStatus.objects.all()
        print(alarm_status)
        return Response('hello')
