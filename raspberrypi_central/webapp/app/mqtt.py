from celery import Celery
import paho.mqtt.client as mqtt
import os
import json
from pathlib import Path
import uuid


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

    celery_client.send_task('security.camera_motion_detected', kwargs=data)

def on_motion_picture(client, userdata, msg):
    random = uuid.uuid4()
    file_path = Path(f'./pictures/{random}.jpg').resolve()

    with open(file_path, 'wb+') as file:
        file.write(msg.payload)

    data = {
        # 'device_id': payload['device_id'],
        'file_path': str(file_path)
    }

    celery_client.send_task('security.camera_motion_picture', kwargs=data)


mqtt_client.subscribe('motion/camera', qos=1)
mqtt_client.message_callback_add('motion/camera', on_motion_camera)
mqtt_client.message_callback_add('motion/picture', on_motion_picture)

mqtt_client.loop_forever()
