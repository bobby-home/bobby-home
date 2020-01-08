from rest_framework import serializers
from .models import Location

class LocationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('structure', 'sub_structure')
