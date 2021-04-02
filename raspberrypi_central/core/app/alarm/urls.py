import io

from django.http import StreamingHttpResponse
from django.urls import include, path

from utils.mqtt import mqtt_factory, MQTT

from alarm.views.alarm_status_views import AlarmStatusUpdate, AlarmStatusCreate, AlarmStatusDetail, \
    AlarmScheduleUpdate, AlarmScheduleCreate, AlarmScheduleDetail
from camera.views.camera_motion_views import CameraMotionDetectedList, CameraMotionDetectedDetail
from camera.views.camera_roi_views import CameraROICreate, CameraROIUpdate, CameraROIList, CameraROIDelete
from alarm.views.alarm_status_views import AlarmHome

app_name = 'alarm'

class HttpStreamMQTT:
    BOUNDARY = 'frame'

    def __init__(self):
        print('create HttpStreamMQTT')
        self._picture = None
        self._mqtt = self._mqtt_init()

    def _mqtt_init(self) -> MQTT:
        mqtt = mqtt_factory(client_id='test_streaming')
        mqtt.client.subscribe(f'ia/picture/+', qos=0)
        mqtt.client.message_callback_add(f'ia/picture/+', self._frame_receiver)

        return mqtt

    def _frame_receiver(self, _client, _userdata, message):
        self._picture = io.BytesIO(message.payload).getvalue()

    def produce(self):
        while True:
            self._mqtt.client.loop()
            print(f'produce stream {self._picture is not None}')
            if self._picture:
                yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + self._picture + b'\r\n\r\n')
                self._picture = None

    def __del__(self):
        print('delete http stream mqtt')

stream = None

def get_image(_request):
    global stream

    if stream is None:
        stream = HttpStreamMQTT()

    return StreamingHttpResponse(stream.produce(), content_type=f"multipart/x-mixed-replace;boundary=frame")


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

urlpatterns = [
    path('stream.jpg', get_image),
    path('', AlarmHome.as_view(), name='home'),
    path('', include(status_patterns)),
    path('schedule/', include(schedule_patterns)),
    path('camera_roi/', include(roi_patterns)),
    path('camera_motion/', include(motions_pattern)),
]
