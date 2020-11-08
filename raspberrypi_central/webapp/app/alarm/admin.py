from django.contrib import admin

import alarm.models.alarm
import alarm.models.camera
from . import models

admin.site.register(alarm.models.alarm.AlarmStatus)
admin.site.register(alarm.models.alarm.AlarmSchedule)
admin.site.register(alarm.models.camera.CameraMotionDetected)
admin.site.register(alarm.models.camera.CameraMotionDetectedPicture)
admin.site.register(alarm.models.camera.CameraRectangleROI)
