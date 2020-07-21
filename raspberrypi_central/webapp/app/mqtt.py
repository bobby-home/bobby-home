from celery import Celery
import paho.mqtt.client as mqtt
import os


def create_mqtt_client(mqtt_user: str, mqtt_pswd: str, mqtt_hostname: str, mqtt_port: str):
    client = mqtt.Client()
    client.username_pw_set(mqtt_user, mqtt_pswd)

    client.connect(mqtt_hostname, int(mqtt_port), keepalive=120)

    return client

mqtt_client = create_mqtt_client(
    os.environ['MQTT_USER'],
    os.environ['MQTT_PASSWORD'],
    os.environ['MQTT_HOSTNAME'],
    os.environ['MQTT_PORT']
)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def on_motion_camera(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    celery_client.send_task('security.camera_motion_detected', kwargs={'device_id': 'some device id here'})

mqtt_client.subscribe('motion/camera')

mqtt_client.message_callback_add('motion/camera', on_motion_camera)

mqtt_client.loop_forever()
