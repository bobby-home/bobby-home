import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from celery import Celery
import paho.mqtt.client as mqtt
import os
import json
from pathlib import Path

from alarm.tasks import camera_motion_picture, camera_motion_detected


celery_client = Celery('tasks', broker='amqp://admin:mypass@rabbit:5672')


def create_mqtt_client(mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
    client = mqtt.Client(client_id='rpi4-mqtt-listen-django', clean_session=False)
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    return client

mqtt_client = create_mqtt_client(
    os.environ['MQTT_USER'],
    os.environ['MQTT_PASSWORD'],
    os.environ['MQTT_HOSTNAME'],
    os.environ['MQTT_PORT']
)


"""
Send the status when executing the script.
So, If some devices are connected before the execution of this script
(i.e this script crashed)
They still receive the status.
"""
on_status_alarm(mqtt_client, None, None)
on_status_sound(mqtt_client, None, None)


mqtt_client.loop_forever()
