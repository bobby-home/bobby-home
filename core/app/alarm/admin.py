from alarm.forms import AlarmStatusForm
from django.contrib import admin
from alarm.models import AlarmStatus, AlarmSchedule, HTTPAlarmStatus, Ping


class AlarmStatusAdmin(admin.ModelAdmin):
    form = AlarmStatusForm

    def save_model(self, request, obj, form, change):
        # save is done through form.
        pass


admin.site.register(AlarmStatus, AlarmStatusAdmin)
admin.site.register(HTTPAlarmStatus)
admin.site.register(AlarmSchedule)
admin.site.register(Ping)
