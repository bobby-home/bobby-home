import io
import time

from django.http import StreamingHttpResponse
from django.urls import include, path

from alarm.views.alarm_status_views import AlarmStatusList, AlarmStatusUpdate, AlarmStatusCreate
from utils.mqtt import mqtt_factory, MQTT

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
    path('', AlarmStatusList.as_view(), name='status-list'),
    path('<int:pk>/edit', AlarmStatusUpdate.as_view(), name='status-edit'),
    path('add', AlarmStatusCreate.as_view(), name='status-add')
]

urlpatterns = [
    path('status/', include(status_patterns)),
    path('stream.jpg', get_image),
]
