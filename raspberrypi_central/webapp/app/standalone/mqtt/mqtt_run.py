import os, sys
import django

sys.path.append('/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from standalone.mqtt import MqttConfig, MQTT
from alarm.mqtt import register

if __name__ == '__main__':
    mqttConfig = MqttConfig(
        client_id='hello-world',
        user=os.environ['MQTT_USER'],
        password=os.environ['MQTT_PASSWORD'],
        hostname=os.environ['MQTT_HOSTNAME'],
        port=os.environ['MQTT_PORT']
    )

    mqtt = MQTT(mqttConfig)
    print('HEY')

    register(mqtt)

    mqtt._client.loop_forever()
