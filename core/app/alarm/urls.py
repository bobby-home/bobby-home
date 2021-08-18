from django.urls import include, path

from alarm.views.alarm_status_views import AlarmStatusUpdate, AlarmStatusCreate, AlarmStatusDetail, \
    AlarmScheduleUpdate, AlarmScheduleCreate, AlarmScheduleDetail
from camera.views.camera_motion_views import CameraMotionDetectedList, CameraMotionDetectedDetail
from camera.views.camera_roi_views import CameraROICreate, CameraROIUpdate, CameraROIList, CameraROIDelete
from alarm.views.alarm_status_views import AlarmHome
from alarm.views.schedule_range_views import AlarmScheduleRangeCreate, AlarmScheduleRangeDetail, AlarmScheduleRangeUpdate


app_name = 'alarm'


status_patterns = [
    path('<int:pk>/edit', AlarmStatusUpdate.as_view(), name='status-edit'),
    path('add', AlarmStatusCreate.as_view(), name='status-add'),
    path('<int:pk>', AlarmStatusDetail.as_view(), name='status-detail')
]


schedule_patterns = [
    path('<int:pk>/edit', AlarmScheduleUpdate.as_view(), name='schedule-edit'),
    path('add', AlarmScheduleCreate.as_view(), name='schedule-add'),
    path('<int:pk>', AlarmScheduleDetail.as_view(), name='schedule-detail')
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

absence_patterns = [
    path('add', AlarmScheduleRangeCreate.as_view(), name='absence-add'),
    path('<int:pk>', AlarmScheduleRangeDetail.as_view(), name='absence-detail'),
    path('<int:pk>/edit', AlarmScheduleRangeUpdate.as_view(), name='absence-edit')
]

urlpatterns = [
    path('', AlarmHome.as_view(), name='home'),
    path('', include(status_patterns)),
    path('schedule/', include(schedule_patterns)),
    path('absence/', include(absence_patterns)),
    path('camera_roi/', include(roi_patterns)),
    path('camera_motion/', include(motions_pattern)),
]
