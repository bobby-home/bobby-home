from django.urls import include, path

from camera.views.camera_motion_views import CameraMotionDetectedList, CameraMotionDetectedDetail
from camera.views.camera_roi_views import CameraROICreate, CameraROIDelete, CameraROIUpdate, CameraROIList

app_name = 'camera'

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
    path('roi/', include(roi_patterns)),
    path('motion/', include(motions_pattern)),
]
