class SpeakerMessaging():
    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    def publish_speaker_status(self, device_id: str, status: bool):
        self._mqtt_client.publish(f'status/speaker/{device_id}', status, retain=True, qos=1)


class AlarmMessaging():

    def __init__(self, mqtt_client, speaker_messaging: SpeakerMessaging):
        self._mqtt_client = mqtt_client
        self._speaker_messaging = speaker_messaging

    def publish_alarm_status(self, device_id: str, status: bool):
        self._mqtt_client.publish(f'status/camera/{device_id}', status, retain=True, qos=1)

        if status is False:
            self._speaker_messaging.publish_speaker_status(device_id, False)


def alarm_messaging_factory(mqtt_client):
    speaker = SpeakerMessaging(mqtt_client)
    return AlarmMessaging(mqtt_client, speaker)
