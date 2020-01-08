from django.contrib import admin

# Register your models here.
from .models import Location, DeviceType, Device, SensorInformation, Sensor

admin.site.register(Location)
admin.site.register(DeviceType)
admin.site.register(Device)
admin.site.register(SensorInformation)
admin.site.register(Sensor)
