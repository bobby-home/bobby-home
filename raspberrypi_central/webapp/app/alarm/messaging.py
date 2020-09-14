class AlarmMessaging():

    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    def publish_alarm_status(self, device_id: str, status: bool):
        self._mqtt_client.publish(f'status/camera/{device_id}', status, retain=True, qos=1)

        if status is False:
            self.publish_sound_status(False)

    def publish_sound_status(self, status: bool):
        # TODO: adapt to the new thing
        self._mqtt_client.publish('status/sound', status, retain=True, qos=1)
