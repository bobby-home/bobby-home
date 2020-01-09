from rest_framework import serializers
from .models import Location, Attachment

class LocationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('structure', 'sub_structure')

class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Attachment
        fields = "__all__"
