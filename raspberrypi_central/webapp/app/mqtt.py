from celery import Celery
import paho.mqtt.client as mqtt
import os
import json
from pathlib import Path
import uuid
from django.core.files.storage import FileSystemStorage
from tasks import camera_motion_picture, camera_motion_detected

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from alarm.models import AlarmStatus

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

def on_motion_camera(client, userdata, msg):
    payload = json.loads(msg.payload)

    data = {
        'device_id': payload['device_id']
    }

    camera_motion_detected.apply_async(kwargs=data)

def on_motion_picture(client, userdata, msg):
    random = uuid.uuid4()
    file_name = f'{random}.jpg'

    with FileSystemStorage.open(file_name, 'wb+') as file:
        file.write(msg.payload)

        data = {
            # 'device_id': payload['device_id'],
            'picture_path': str(file.name)
        }

        camera_motion_picture.apply_async(kwargs=data)


def on_status_alarm(client, userdata, msg):
    alarm_status = AlarmStatus.objects.get(pk=1)
    status = alarm_status.running

    client.publish('/something/else', payload=str(status), qos=1)

mqtt_client.subscribe('motion/#', qos=1)
mqtt_client.message_callback_add('motion/camera', on_motion_camera)
mqtt_client.message_callback_add('motion/picture', on_motion_picture)

mqtt_client.subscribe('ask/#', qos=1)
mqtt_client.message_callback_add('ask/status/alarm', on_status_alarm)

"""
Send the status when executing the script.
So, If some devices are connected before the execution of this script
(i.e this script crashed)
They still receive the status.
"""
on_status_alarm(mqtt_client, None, None)

mqtt_client.loop_forever()
