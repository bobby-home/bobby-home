from django.contrib import admin
from . import models

admin.site.register(models.AlarmStatus)
admin.site.register(models.AlarmSchedule)
admin.site.register(models.CameraMotionDetected)
admin.site.register(models.CameraMotionDetectedPicture)
