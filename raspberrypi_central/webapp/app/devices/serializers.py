from rest_framework import serializers
from .models import Locations

class LocationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Locations
        fields = ('structure', 'sub_structure')
