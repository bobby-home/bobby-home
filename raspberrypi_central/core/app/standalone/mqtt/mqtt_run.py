import sys
sys.path.append('/usr/src/app')

from utils.django.standalone_init import init
init()


from utils.mqtt import mqtt_factory  # noqa: E402
from alarm.mqtt import register  # noqa: E402

mqtt = mqtt_factory(client_id='python_process_mqtt')

register(mqtt)

mqtt.client.loop_forever()
