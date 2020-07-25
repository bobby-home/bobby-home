from celery import Celery
import paho.mqtt.client as mqtt
import os
import json
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

    # @TODO
    celery_client.send_task('security.camera_motion_detected', kwargs=data)

def on_status_alarm(client, userdata, msg):
    alarm_status = AlarmStatus.objects.get(pk=1)
    client.publish('/something/else', payload=str(alarm_status), qos=1)


mqtt_client.subscribe('motion/#', qos=1)
mqtt_client.message_callback_add('motion/camera', on_motion_camera)

mqtt_client.subscribe('ask/#', qos=1)
mqtt_client.message_callback_add('ask/status/alarm', on_status_alarm)

mqtt_client.loop_forever()
