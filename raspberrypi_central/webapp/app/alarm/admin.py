from django.contrib import admin

from alarm.models import AlarmStatus, AlarmSchedule

admin.site.register(AlarmStatus)
admin.site.register(AlarmSchedule)
