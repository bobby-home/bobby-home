from django.shortcuts import render
from rest_framework import viewsets

from .serializers import LocationsSerializer
from .models import Locations

class LocationsViewSet(viewsets.ModelViewSet):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer
