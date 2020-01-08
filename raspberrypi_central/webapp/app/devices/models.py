from django.db import models
from django.contrib.postgres.fields import JSONField


class Location(models.Model):
    structure = models.CharField(max_length=60)
    sub_structure = models.CharField(max_length=60)


class DeviceType(models.Model):
    '''
    RaspberryPI4, zero w, zero, arduino uno, esp8266...
    '''
    type = models.CharField(max_length=100, unique=True)


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True)
    location = models.ForeignKey('Location', on_delete=models.PROTECT)
    device_type = models.ForeignKey('DeviceType', on_delete=models.PROTECT)

class SensorInformation(models.Model):
    TEMPERATURE = 0
    LIGHT = 1
    MOTION = 2
    ULTRA_SONIC = 3

    TYPE_CHOICES = [
        (TEMPERATURE, 'temperature'),
        (LIGHT, 'light'),
        (MOTION, 'motion'),
        (ULTRA_SONIC, 'ultra sonic')
    ]

    type = models.IntegerField(choices=TYPE_CHOICES)
    reference = models.CharField(max_length=100)

class Sensor(models.Model):
    sensor_information = models.ForeignKey('SensorInformation', on_delete=models.PROTECT)
    device = models.ForeignKey('Device', on_delete=models.PROTECT)


class SensorData(models.Model):
    received_at = models.DateTimeField(editable=False)
    # JSONField uses jsonb pgsql data type.
    data = JSONField()
    sensor = models.ForeignKey('Sensor', on_delete=models.PROTECT)


    # from https://stackoverflow.com/a/1737078
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.received_at = timezone.now()
        # else: lock the update?! Raise an error here?
        return super(SensorData, self).save(*args, **kwargs)
