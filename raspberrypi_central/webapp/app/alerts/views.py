from api_keys.permissions import HasAPIAccess
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics, mixins

from . import serializers
from . import models

class AttachmentViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):

    queryset = models.Attachment.objects.all()
    serializer_class = serializers.AttachmentSerializer

class AlertTypeViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):

    queryset = models.AlertType.objects.all()
    serializer_class = serializers.AlertTypeSerializer

class AlertViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    queryset = models.Alert.objects.all()
    serializer_class = serializers.AlertSerializer
