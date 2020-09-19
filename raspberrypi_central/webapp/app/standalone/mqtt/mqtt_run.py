import os
import sys
import django

sys.path.append('/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()


from utils.mqtt import mqtt_factory  # noqa: E402
from alarm.mqtt import register  # noqa: E402

mqtt = mqtt_factory(client_id='hello-world')

register(mqtt)

mqtt._client.loop_forever()
