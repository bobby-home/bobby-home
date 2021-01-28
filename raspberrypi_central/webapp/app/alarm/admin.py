from django.contrib import admin

from alarm.business.alarm_status import alarm_status_changed
from alarm.models import AlarmStatus, AlarmSchedule

class AlarmStatusAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        alarm_status_changed(obj)

admin.site.register(AlarmStatus, AlarmStatusAdmin)
admin.site.register(AlarmSchedule)
