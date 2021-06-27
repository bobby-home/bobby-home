from alarm.mqtt import MqttServices
from camera.messaging import CameraMessaging, camera_messaging_factory
from utils.mqtt.mqtt_status import MqttBooleanStatus, MqttJsonStatus

from camera.messaging import CameraData


class SpeakerMessaging:
    def __init__(self, mqtt_status: MqttBooleanStatus):
        self._mqtt_status = mqtt_status

    def publish_speaker_status(self, device_id: str, status: bool):
        self._mqtt_status.publish(f'status/{MqttServices.SPEAKER.value}/{device_id}', status)


class AlarmMessaging:
    """Class to communicate with Alarm services (through mqtt).
    """
    def __init__(self, mqtt_status: MqttJsonStatus, speaker_messaging: SpeakerMessaging, camera_messaging: CameraMessaging):
        self._mqtt_status = mqtt_status
        self._speaker_messaging = speaker_messaging
        self._camera_messaging = camera_messaging

    def publish_alarm_status(self, device_id: str, device_type: str, status: bool) -> None:
        # why 2 publish call????
        # I guess it's because I can stream my camera without starting up the object_detection for it.
        # but in this case, I could use the same topic because I have the info, "to_analyze",
        # if set to False, don't start a new object detection object for it.

        # todo: check if device supports video, if not flag it.
        camera_data = CameraData(to_analyze=True) if status else CameraData(to_analyze=False)
        
        if device_type == 'esp32cam':
            camera_data.video_support = False

        #self._mqtt_status.publish(f'status/{MqttServices.OBJECT_DETECTION_MANAGER.value}/{device_id}', status, camera_data)

        # will send to camera_manager
        self._camera_messaging.publish_status(device_id, status, camera_data)

        if status is False:
            self._speaker_messaging.publish_speaker_status(device_id, False)


def speaker_messaging_factory(mqtt_client):
    mqtt_status = MqttBooleanStatus(mqtt_client)

    return SpeakerMessaging(mqtt_status)


def alarm_messaging_factory(mqtt_client):
    mqtt_status = MqttJsonStatus(mqtt_client)
    speaker = speaker_messaging_factory(mqtt_client)
    camera = camera_messaging_factory(mqtt_client)

    return AlarmMessaging(mqtt_status, speaker, camera)
