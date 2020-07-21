from __future__ import absolute_import, unicode_literals
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from celery import shared_task
import paho.mqtt.client as mqtt
import os


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
        self.client.publish(self.mqtt_alarm_camera_topic, status)

@shared_task
def alarm_messaging(status: bool):
    alarm_messaging = AlarmMessaging(
        os.environ['MQTT_USER'],
        os.environ['MQTT_PASSWORD'],
        os.environ['MQTT_HOSTNAME'],
        os.environ['MQTT_PORT'],
        os.environ['MQTT_ALARM_CAMERA_TOPIC'])

    alarm_messaging.set_status(status)


TOKEN=os.environ['TELEGRAM_BOT_TOKEN']

@shared_task
def send_telegram_message(msg: str, picture_path = None):
    updater = Updater(TOKEN, use_context=True)
    bot = updater.bot

    bot.send_message(chat_id="749348319", text=msg)

    if picture_path:
        bot.send_photo(chat_id="749348319", photo=open(picture_path, 'rb'))

@shared_task(name="security.camera_motion_detected")
def camera_motion_detected(device_id: str):
    send_telegram_message.apply_async(args=['Une présence étrangère a été détectée chez vous.'])
