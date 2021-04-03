from django.urls import include, path

from camera.views.camera_motion_views import CameraMotionDetectedList, CameraMotionDetectedDetail, CameraStreamDetail
from camera.views.camera_roi_views import CameraROICreate, CameraROIDelete, CameraROIUpdate, CameraROIList
from camera.views.steam import stream_answer

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

streaming_pattern = [
]

urlpatterns = [
    path('<int:pk>/stream', CameraStreamDetail.as_view(), name='camera_stream-detail'),
    path('<int:pk>/stream/flux.jpg', stream_answer, name='camera_stream'),

    path('roi/', include(roi_patterns)),
    path('motion/', include(motions_pattern)),
]
