import os

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from celery import shared_task
import paho.mqtt.client as mqtt

from alarm import models as alarm_models
from house import models as house_models
from devices import models as device_models
from notification.tasks import send_message


def create_mqtt_client(mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str, client_name = None):

    if client_name is None:
        clean_session = True
    else:
        False

    client = mqtt.Client(client_id=client_name, clean_session=client_name)
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    return client


class AlarmMessaging():

    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    def set_alarm_status(self, status: bool):
        self._mqtt_client.publish('status/alarm', status, qos=1)

        if status is False:
            self.set_sound_status(False)

    def set_sound_status(self, status: bool):
        self._mqtt_client.publish('status/sound', status, qos=1)


@shared_task(name="security.camera_motion_picture", bind=True)
def camera_motion_picture(self, picture_path):
    picture = alarm_models.CameraMotionDetectedPicture(picture_path=picture_path)
    picture.save()

    kwargs = {
        'picture_path': picture_path
    }
    send_message.apply_async(kwargs=kwargs)


@shared_task(name="security.play_sound")
def play_sound(motion_came_from_device_id: str):
    # device = device_models.Device.objects.get(device_id=device_id)
    mqtt_client = create_mqtt_client(
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT']
    )

    alarm_messaging = AlarmMessaging(mqtt_client)
    alarm_messaging.set_sound_status(True)


@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str):
    device = device_models.Device.objects.get(device_id=device_id)
    alarm_models.CameraMotionDetected.objects.create(device=device)

    location = device.location

    kwargs = {
        'message': f'Une présence étrangère a été détectée chez vous depuis {device_id} {location.structure} {location.sub_structure}'
    }

    send_message.apply_async(kwargs=kwargs)
    play_sound.apply_async(kwargs={'motion_came_from_device_id': device_id})


@shared_task(name="alarm.set_alarm_off")
def set_alarm_off():
    s = alarm_models.AlarmStatus(running=False)
    s.save()


@shared_task(name="alarm.set_alarm_on")
def set_alarm_on():
    s = alarm_models.AlarmStatus(running=True)
    s.save()


@shared_task
def alarm_status_changed(status: bool):
    mqtt_client = create_mqtt_client(
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT']
    )

    alarm_messaging = AlarmMessaging(mqtt_client)
    alarm_messaging.set_alarm_status(status)

    kwargs = {
        'message': f'Votre alarme a changée de status: {status}'
    }
    send_message.apply_async(kwargs=kwargs)
