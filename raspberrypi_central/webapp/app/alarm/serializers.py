from rest_framework import serializers
from . import models

class AlarmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AlarmStatus
        fields = ['id', 'running']
