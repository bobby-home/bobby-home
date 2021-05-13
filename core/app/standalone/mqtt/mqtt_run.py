import sys
sys.path.append('/usr/src/app')

from utils.django.standalone_init import init
init()

from utils.mqtt.mqtt_status_handler import on_connected_services
from utils.mqtt.mqtt_update_status import on_updates
from utils.mqtt import mqtt_factory  # noqa: E402
from alarm.mqtt import SERVICES, UPDATES  # noqa: E402
from alarm.mqtt.mqtt_controller import register

mqtt = mqtt_factory(client_id='python_process_mqtt')

on_connected_services(mqtt, SERVICES)
on_updates(mqtt, UPDATES)
register(mqtt)

mqtt.client.loop_forever()
