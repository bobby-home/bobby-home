from rest_framework import serializers
from . import models

class AlarmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AlarmStatus
        fields = "__all__"

    def update(self, validated_data):
        return AlarmStatus.objects.update_or_create(
            is_active=validated_data.get('is_active')
        )
