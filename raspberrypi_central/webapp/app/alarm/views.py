from django.shortcuts import render
from api_keys.permissions import HasAPIAccess
from rest_framework import viewsets, generics, mixins
from . import serializers
from . import models


class AlarmStatusViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AlarmStatus.objects.all()
    serializer_class = serializers.AlarmStatusSerializer

