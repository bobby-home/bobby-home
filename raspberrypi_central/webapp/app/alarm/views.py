from django.shortcuts import render
from api_keys.permissions import HasAPIAccess
from rest_framework import viewsets, generics, mixins
from . import serializers
from . import models

from django.shortcuts import render


def index(request):
    status = models.AlarmStatus.objects.all()

    context = {'status': status}
    return render(request, 'home.html', context)


class AlarmStatusViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AlarmStatus.objects.all()
    serializer_class = serializers.AlarmStatusSerializer
