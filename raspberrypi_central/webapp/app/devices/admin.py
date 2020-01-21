from django.contrib import admin

# Register your models here.
from .models import Location, DeviceType, Device, SensorInformation, Sensor

class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('device_id',)

admin.site.register(Location)
admin.site.register(DeviceType)
admin.site.register(Device, DeviceAdmin)
admin.site.register(SensorInformation)
admin.site.register(Sensor)
