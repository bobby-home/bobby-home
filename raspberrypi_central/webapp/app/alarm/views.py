from django.shortcuts import render
from api_keys.permissions import HasAPIAccess
from rest_framework import viewsets, generics, mixins, status
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from . import models
from . import tasks

from django.shortcuts import render


def index(request):
    status = models.AlarmStatus.objects.all()

    context = {'status': status}
    return render(request, 'alarm/schedule.html', context)

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
