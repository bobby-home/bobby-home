import sys
sys.path.append('/usr/src/app')

from utils.django.standalone_init import init
init()

from utils.mqtt.mqtt_status_handler import on_connected_services
from utils.mqtt import mqtt_factory  # noqa: E402
from alarm.mqtt import register, SERVICES  # noqa: E402


mqtt = mqtt_factory(client_id='python_process_mqtt')

on_connected_services(mqtt, SERVICES)
register(mqtt)

mqtt.client.loop_forever()
