import io
from typing import Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from alarm.models import AlarmStatus
from camera.messaging import CameraMessaging, camera_messaging_factory, CameraData
from utils.mqtt import mqtt_factory, MQTT


class HttpStreamMQTT:
    BOUNDARY = 'frame'

    def __init__(self, alarm: AlarmStatus):
        self._picture = None
        self._alarm = alarm
        self._mqtt, self._camera_messaging = self._mqtt_init()
        self._consecutive_failures = 0

    def _mqtt_init(self) -> Tuple[MQTT, CameraMessaging]:
        mqtt = mqtt_factory()
        mqtt.client.subscribe(f'camera/stream/{self._alarm.device.device_id}', qos=0)
        mqtt.client.message_callback_add(f'camera/stream/{self._alarm.device.device_id}', self._frame_receiver)

        camera_messaging = camera_messaging_factory(mqtt)
        camera_messaging.publish_status(self._alarm.device.device_id, True, CameraData(stream=True))

        return mqtt, camera_messaging

    def _frame_receiver(self, _client, _userdata, message):
        self._picture = io.BytesIO(message.payload).getvalue()

    def produce(self):
        # ~25 frame per seconds, if it does not receive any frame for ~8s it stops the loop
        # and thus stop the stream.
        while True and self._consecutive_failures < 25*8:
            self._mqtt.client.loop()
            if self._picture:
                self._consecutive_failures = 0
                yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + self._picture + b'\r\n\r\n')
                self._picture = None
            else:
                self._consecutive_failures += 1

    def __del__(self):
        # query because AlarmStatus could have turned off during the stream.
        alarm = AlarmStatus.objects.get(pk=self._alarm.pk)

        if alarm.running is False:
            self._camera_messaging.publish_status(self._alarm.device.device_id, False, CameraData(stream=False))
        else:
            self._camera_messaging.publish_status(self._alarm.device.device_id, True, CameraData(stream=False))

class CameraStreamingHttpResponse(StreamingHttpResponse):
    def __init__(self, stream: HttpStreamMQTT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stream = stream

    def close(self):
        super().close()
        # we need to manually delete the object to stop the background thread
        # and close mqtt connections that listen for frames.
        self._stream.__del__()


def stream_answer(_request, pk):
    alarm = get_object_or_404(AlarmStatus, id=pk)
    stream = HttpStreamMQTT(alarm)

    return CameraStreamingHttpResponse(stream, stream.produce(), content_type=f"multipart/x-mixed-replace;boundary=frame")


class CameraStreamDetail(LoginRequiredMixin, DetailView):
    model = AlarmStatus
    template_name = 'camera/camera_stream.html'

    context_object_name = 'camera'
