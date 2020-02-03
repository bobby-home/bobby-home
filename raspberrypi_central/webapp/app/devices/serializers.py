from rest_framework import serializers
from . import models

class LocationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Location
        fields = '__all__'

