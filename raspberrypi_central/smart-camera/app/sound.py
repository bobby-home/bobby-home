import os

from mqtt.mqtt_client import get_mqtt
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from sound.run_sound import run_sound_factory
from thread.thread_manager import ThreadManager


device_id = os.environ['DEVICE_ID']

sound_mqtt_client = get_mqtt(f"{device_id}-sound")

sound_manager = ThreadManager(run_sound_factory())
mqtt_status_manage_thread_factory(device_id, 'speaker', sound_mqtt_client, sound_manager, status_json=False)

sound_mqtt_client.client.loop_forever()
