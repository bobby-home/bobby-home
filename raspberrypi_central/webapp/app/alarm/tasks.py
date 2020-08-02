from __future__ import absolute_import, unicode_literals
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from celery import shared_task
import paho.mqtt.client as mqtt
import os

from alarm import models as alarm_models
from house import models as house_models

from alarm.messaging import Messaging

class AlarmMessaging():

    def __init__(self, mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str, mqtt_alarm_camera_topic):
        self.mqtt_user = mqtt_user
        self.mqtt_pswd = mqtt_pswd
        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port
        self.mqtt_alarm_camera_topic = mqtt_alarm_camera_topic

        self.client = self._mqtt_connect()

    def _mqtt_connect(self):
        client = mqtt.Client()
        client.username_pw_set(self.mqtt_user, self.mqtt_pswd)

        client.connect(self.mqtt_hostname, int(self.mqtt_port), keepalive=120)

        return client
    
    def set_status(self, status: bool):
        self.client.publish(self.mqtt_alarm_camera_topic, status, qos=1)


@shared_task
def alarm_messaging(status: bool):
    alarm_messaging = AlarmMessaging(
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT'],
        os.environ['MQTT_ALARM_CAMERA_TOPIC'])

    alarm_messaging.set_status(status)


@shared_task
def send_message(msg: str):
    messaging = Messaging()
    messaging.send_message(msg)


@shared_task(name="security.camera_motion_picture")
def camera_motion_picture(picture_path):
    messaging = Messaging()
    messaging.send_message(picture_path=file_path)


@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str):
    send_message.apply_async(args=[f'Une présence étrangère a été détectée chez vous depuis {device_id}'])


@shared_task(name="alarm.set_alarm_off")
def set_alarm_off():
    s = alarm_models.AlarmStatus(running=False)
    s.save()


@shared_task(name="alarm.set_alarm_on")
def set_alarm_on():
    s = alarm_models.AlarmStatus(running=True)
    s.save()
