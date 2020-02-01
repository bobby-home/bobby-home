from rest_framework import serializers
from .models import Location, Attachment, Alert, AlertType


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

class AlertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertType
        fields = "__all__"

class AlertSerializer(serializers.ModelSerializer):
    # alert_type = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='type'
    # )

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Alert
        fields = "__all__"
