from django.urls import include, path

from alarm.views.alarm_status_views import AlarmStatusList, AlarmStatusUpdate, AlarmStatusCreate
from alarm.views.camera_motion_views import CameraMotionDetectedList, CameraMotionDetectedDetail
from alarm.views.camera_roi_views import CameraROICreate, CameraROIUpdate, CameraROIList, CameraROIDelete

app_name = 'alarm'

status_patterns = [
    path('', AlarmStatusList.as_view(), name='status-list'),
    path('<int:pk>/edit', AlarmStatusUpdate.as_view(), name='status-edit'),
    path('add', AlarmStatusCreate.as_view(), name='status-add')
]

roi_patterns = [
    path('', CameraROIList.as_view(), name='camera_roi-list'),
    path('<int:pk>/edit', CameraROIUpdate.as_view(), name='camera_roi-edit'),
    path('<int:pk>/delete', CameraROIDelete.as_view(), name='camera_roi-delete'),
    path('add', CameraROICreate.as_view(), name='camera_roi-add'),
]

motions_pattern = [
    path('', CameraMotionDetectedList.as_view(), name='camera_motion_detected-list'),
    path('<int:pk>', CameraMotionDetectedDetail.as_view(), name='camera_motion_detected-detail'),
]

urlpatterns = [
    path('status/', include(status_patterns)),
    path('camera_roi/', include(roi_patterns)),
    path('camera_motion/', include(motions_pattern)),
]
