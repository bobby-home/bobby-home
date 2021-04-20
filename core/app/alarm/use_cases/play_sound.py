from celery import shared_task

from alarm.messaging import speaker_messaging_factory
from utils.mqtt import mqtt_factory


@shared_task(name="security.play_sound")
def play_sound(device_id: str, status: bool = True):
    mqtt_client = mqtt_factory()

    speaker = speaker_messaging_factory(mqtt_client)
    speaker.publish_speaker_status(device_id, status)
