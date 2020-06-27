from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Location)
admin.site.register(models.DeviceType)
admin.site.register(models.Device)
# admin.site.register(SensorInformation)
# admin.site.register(Sensor)
