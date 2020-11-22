from django.contrib import admin

from .models.camera import CameraROI, CameraRectangleROI, CameraMotionDetectedPicture, CameraMotionDetected, \
    CameraMotionDetectedBoundingBox
from .models.alarm import AlarmStatus, AlarmSchedule

admin.site.register(AlarmStatus)
admin.site.register(AlarmSchedule)

admin.site.register(CameraMotionDetected)
admin.site.register(CameraMotionDetectedPicture)
admin.site.register(CameraRectangleROI)
admin.site.register(CameraROI)
admin.site.register(CameraMotionDetectedBoundingBox)
