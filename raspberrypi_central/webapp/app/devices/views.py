from django.shortcuts import render
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from api_keys.permissions import HasAPIAccess

from . import serializers
from . import models


class LocationsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationsSerializer
