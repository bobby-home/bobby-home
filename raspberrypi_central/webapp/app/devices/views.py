from django.shortcuts import render
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from api_keys.permissions import HasAPIAccess

from .serializers import LocationsSerializer, AttachmentSerializer, AlertSerializer, AlertTypeSerializer
from .models import Location, Attachment, Alert, AlertType


class LocationsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    
    queryset = Location.objects.all()
    serializer_class = LocationsSerializer

class AttachmentViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):

    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

class AlertTypeViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):

    queryset = AlertType.objects.all()
    serializer_class = AlertTypeSerializer

class AlertViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
