import io
from typing import Tuple

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404

from alarm.models import AlarmStatus
from camera.messaging import CameraMessaging, camera_messaging_factory, CameraData
from utils.mqtt import mqtt_factory, MQTT


class HttpStreamMQTT:
    BOUNDARY = 'frame'

    def __init__(self, alarm: AlarmStatus):
        print('create HttpStreamMQTT')
        self._picture = None
        self._alarm = alarm
        self._mqtt, self._camera_messaging = self._mqtt_init()

    def _mqtt_init(self) -> Tuple[MQTT, CameraMessaging]:
        mqtt = mqtt_factory(client_id='test_streaming')
        mqtt.client.subscribe(f'camera/stream/+', qos=0)
        mqtt.client.message_callback_add(f'camera/stream/+', self._frame_receiver)

        camera_messaging = camera_messaging_factory(mqtt)
        camera_messaging.publish_status(self._alarm.device.device_id, True, CameraData(stream=True))

        return mqtt, camera_messaging

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

        # query because AlarmStatus could have turned off during the stream.
        alarm = AlarmStatus.objects.get(pk=self._alarm.pk)

        if alarm.running is False:
            self._camera_messaging.publish_status(self._alarm.device.device_id, False)
        else:
            self._camera_messaging.publish_status(self._alarm.device.device_id, True, CameraData(stream=True))

stream = None

class CameraStreamingHttpResponse(StreamingHttpResponse):
    def __init__(self, stream: HttpStreamMQTT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stream = stream

    def close(self):
        super().close()
        print('close stream')
        self._stream.__del__()


def stream_answer(_request, pk):
    global stream

    alarm = get_object_or_404(AlarmStatus, id=pk)

    stream = HttpStreamMQTT(alarm)

    return CameraStreamingHttpResponse(stream, stream.produce(), content_type=f"multipart/x-mixed-replace;boundary=frame")
