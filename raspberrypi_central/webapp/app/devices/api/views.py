from rest_framework import viewsets
from devices.models import Device
from devices.api.serializers import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


# class LocationsViewSet(viewsets.ModelViewSet):
#     queryset = models.Location.objects.all()
#     serializer_class = serializers.LocationsSerializer
