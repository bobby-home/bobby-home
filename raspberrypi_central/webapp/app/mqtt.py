import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from celery import Celery
import paho.mqtt.client as mqtt
import os
import json
from pathlib import Path
import uuid
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from alarm.tasks import camera_motion_picture, camera_motion_detected
from django.core.files.base import ContentFile

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

    # Remember: image is bytearray
    image = msg.payload

    fs = FileSystemStorage()
    filename = default_storage.save(file_name, ContentFile(image))
    picture_path = default_storage.path(filename)

    data = {
        'picture_path': picture_path
    }

    camera_motion_picture.apply_async(kwargs=data)


def on_status_alarm(client, userdata, msg):
    status = AlarmStatus.objects.get_status()

    client.publish('status/alarm', payload=str(status), qos=1)

def on_status_sound(client, userdata, msg):
    client.publish('status/sound', payload=str(False), qos=1)

def on_motion_camera_no_more(client, userdata, msg):
    client.publish('status/sound', payload=str(False), qos=1)


mqtt_client.subscribe('motion/#', qos=1)
mqtt_client.message_callback_add('motion/camera', on_motion_camera)
mqtt_client.message_callback_add('motion/picture', on_motion_picture)
mqtt_client.message_callback_add('motion/camera/no_more', on_motion_camera_no_more)


mqtt_client.subscribe('ask/#', qos=1)
mqtt_client.message_callback_add('ask/status/alarm', on_status_alarm)
mqtt_client.message_callback_add('ask/status/sound', on_status_sound)

"""
Send the status when executing the script.
So, If some devices are connected before the execution of this script
(i.e this script crashed)
They still receive the status.
"""
# on_status_alarm(mqtt_client, None, None)
# on_status_sound(mqtt_client, None, None)


mqtt_client.loop_forever()
