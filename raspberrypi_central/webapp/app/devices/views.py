from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from api_keys.permissions import HasAPIAccess

from .serializers import LocationsSerializer, AttachmentSerializer
from .models import Location, Attachment

class LocationsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    
    queryset = Location.objects.all()
    serializer_class = LocationsSerializer

# The ListCreateAPIView is a generic view which provides GET (list all) and POST method handlers
class AttachmentView(generics.ListCreateAPIView):
    permission_classes = (HasAPIAccess,)

    """This class defines the create behavior of our rest api."""
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()
