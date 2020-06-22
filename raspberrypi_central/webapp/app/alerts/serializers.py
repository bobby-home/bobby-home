from rest_framework import serializers
from . import models


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = models.Attachment
        fields = "__all__"

class AlertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AlertType
        fields = "__all__"

class AlertSerializer(serializers.ModelSerializer):
    # alert_type = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='type'
    # )

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = models.Alert
        fields = "__all__"
