from rest_framework import serializers
from . import models

class AlarmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AlarmStatus
        fields = ['id', 'running']

    def create(self, validated_data):
        status = validated_data.get('running')
        
        messaging = alarm_messaging_factory()
        messaging.set_status(status)

        # I don't know why, but this doesn't work!
        # I got "Got AttributeError when attempting to get a value for field `running` on serializer"
        # So, I've done this with the old fashion.
        # return models.AlarmStatus.objects.update_or_create(
        #     id=1,
        #     defaults={'running': True}
        # )
        defaults = {'running': status}
        try:
            obj = models.AlarmStatus.objects.get(id='1')
            for key, value in defaults.items():
                setattr(obj, key, value)
            obj.save()
        except models.AlarmStatus.DoesNotExist:
            new_values = {'id': '1'}
            new_values.update(defaults)
            obj = models.AlarmStatus(**new_values)
            obj.save()

        return obj
