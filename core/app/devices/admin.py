from django.contrib import admin
from . import models


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(models.DeviceType)
admin.site.register(models.Device)
