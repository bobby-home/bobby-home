from alarm.models import AlarmStatus
from utils.mqtt import MQTT
import alarm.use_cases.out_alarm as out_alarm
import camera.business.camera_motion as camera_motion
from utils.mqtt.mqtt_status_handler import OnConnectedHandlerLog


class OnConnectedObjectDetection(OnConnectedHandlerLog):

    def __init__(self, client: MQTT):
        super().__init__(client, AlarmStatus)

    def on_connect(self, service_name: str, device_id: str) -> None:
        camera_motion.close_unclosed_camera_motions(device_id)

        return super().on_connect(service_name, device_id)

    def on_disconnect(self, service_name: str, device_id: str) -> None:
        camera_motion.close_unclosed_camera_motions(device_id)

        return super().on_disconnect(service_name, device_id)


class OnConnectedCamera(OnConnectedHandlerLog):
    def __init__(self, client: MQTT):
        super().__init__(client, AlarmStatus)


class OnConnectedCameraManager(OnConnectedHandlerLog):
    def on_connect(self, service_name: str, device_id: str) -> None:
        mx = out_alarm.notify_alarm_status_factory(self.get_client)
        mx.publish_device_connected(device_id)

        return super().on_connect(service_name, device_id)

class OnConnectedSpeakerHandler(OnConnectedHandlerLog):
    pass
