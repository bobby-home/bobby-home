from django.contrib import admin

# Register your models here.
from . import models

class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(models.Location)
admin.site.register(models.DeviceType)
admin.site.register(models.Device, DeviceAdmin)
# admin.site.register(SensorInformation)
# admin.site.register(Sensor)
