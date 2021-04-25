from alarm.models import AlarmStatus
from utils.mqtt import MQTT
import alarm.use_cases.out_alarm as out_alarm
import camera.business.camera_motion as camera_motion
from utils.mqtt.mqtt_status_handler import OnConnectedHandler, OnConnectedHandlerLog, OnConnectedVerifyStatusHandler


class OnConnectedObjectDetection(OnConnectedHandlerLog):
    def __init__(self, *_args, **_kwargs):
        pass

    def on_connect(self, service_name: str, device_id: str) -> None:
        camera_motion.close_unclosed_camera_motions(device_id)

        return super().on_connect(service_name, device_id)

    def on_disconnect(self, service_name: str, device_id: str) -> None:
        camera_motion.close_unclosed_camera_motions(device_id)

        return super().on_disconnect(service_name, device_id)


class OnConnectedCamera(OnConnectedHandler):
    def __init__(self, *_args, **_kwargs):

        # don't verify on_connect because it could be stream.
        # if stream -> camera service is up even if alarm status is not running.
        self._handlers = (
            OnConnectedVerifyStatusHandler(AlarmStatus, on_connect=False),
            OnConnectedHandlerLog(),
        )

    def on_connect(self, service_name: str, device_id: str) -> None:
         for h in self._handlers:
            h.on_connect(service_name, device_id)

    def on_disconnect(self, service_name: str, device_id: str) -> None:
        for h in self._handlers:
            h.on_disconnect(service_name, device_id)


class OnConnectedCameraManager(OnConnectedHandlerLog):
    def __init__(self, mqtt: MQTT) -> None:
        self._mqtt = mqtt

    def on_connect(self, service_name: str, device_id: str) -> None:
        mx = out_alarm.notify_alarm_status_factory(lambda: self._mqtt)
        mx.publish_device_connected(device_id)

        return super().on_connect(service_name, device_id)


class OnConnectedSpeakerHandler(OnConnectedHandlerLog):
    pass
