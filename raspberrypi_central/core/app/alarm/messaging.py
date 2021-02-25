from django.utils import timezone

from utils.mqtt.mqtt_status import MqttBooleanStatus, MqttJsonStatus
from mqtt_services.tasks import verify_service_status


class SpeakerMessaging:
    def __init__(self, mqtt_status: MqttBooleanStatus):
        self._mqtt_status = mqtt_status

    def publish_speaker_status(self, device_id: str, status: bool):
        self._mqtt_status.publish(f'status/speaker/{device_id}', status)


class AlarmMessaging:

    def __init__(self, mqtt_status: MqttJsonStatus, speaker_messaging: SpeakerMessaging, verify_service_status):
        self._mqtt_status = mqtt_status
        self._speaker_messaging = speaker_messaging
        self._verify_service_status = verify_service_status

    def publish_alarm_status(self, device_id: str, status: bool, is_dumb: bool, data=None) -> None:
        self._mqtt_status.publish(f'status/camera/{device_id}', status, data)

        """
        When the system turns on the camera, the object_detection should be up a bit later.
        """

        kwargs = {
            'device_id': device_id,
            'service_name': 'object_detection',
            'status': status,
            'since_time': timezone.now()
        }

        if is_dumb is True and status is False:
            # weird case, the service object_detection does not publish off
            # for dumb cameras.
            pass
        else:
            self._verify_service_status.apply_async(kwargs=kwargs, countdown=15)

        if is_dumb is True:
            kwargs_dumb = {
                'device_id': device_id,
                'service_name': 'dumb_camera',
                'status': status,
                'since_time': timezone.now()
            }
            self._verify_service_status.apply_async(kwargs=kwargs_dumb, countdown=15)

        if status is False:
            self._speaker_messaging.publish_speaker_status(device_id, False)


def speaker_messaging_factory(mqtt_client):
    mqtt_status = MqttBooleanStatus(mqtt_client)

    return SpeakerMessaging(mqtt_status)


def alarm_messaging_factory(mqtt_client):
    mqtt_status = MqttJsonStatus(mqtt_client)
    speaker = speaker_messaging_factory(mqtt_client)

    return AlarmMessaging(mqtt_status, speaker, verify_service_status)
