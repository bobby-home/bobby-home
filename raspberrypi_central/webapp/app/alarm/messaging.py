from utils.mqtt.mqtt_status import MqttBooleanStatus, MqttJsonStatus


class SpeakerMessaging:
    def __init__(self, mqtt_status: MqttBooleanStatus):
        self._mqtt_status = mqtt_status

    def publish_speaker_status(self, device_id: str, status: bool):
        self._mqtt_status.publish(f'status/speaker/{device_id}', status)


class AlarmMessaging:

    def __init__(self, mqtt_status: MqttJsonStatus, speaker_messaging: SpeakerMessaging):
        self._mqtt_status = mqtt_status
        self._speaker_messaging = speaker_messaging

    def publish_alarm_status(self, device_id: str, status: bool, data = None):
        self._mqtt_status.publish(f'status/camera/{device_id}', status, data)

        if status is False:
            self._speaker_messaging.publish_speaker_status(device_id, False)


def speaker_messaging_factory(mqtt_client):
    mqtt_status = MqttBooleanStatus(mqtt_client)

    return SpeakerMessaging(mqtt_status)


def alarm_messaging_factory(mqtt_client):
    mqtt_status = MqttJsonStatus(mqtt_client)
    speaker = speaker_messaging_factory(mqtt_client)

    return AlarmMessaging(mqtt_status, speaker)
