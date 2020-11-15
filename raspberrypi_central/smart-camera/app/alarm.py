import os

from camera.run_camera import run_smart_camera_factory
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from thread.thread_manager import ThreadManager
from mqtt.mqtt_client import get_mqtt

device_id = os.environ['DEVICE_ID']

mqtt_client = get_mqtt(f"{device_id}-rpi4-alarm-motion")

manager = ThreadManager(run_smart_camera_factory())
mqtt_status_manage_thread_factory(device_id, 'camera', mqtt_client, manager, status_json=True)


# def run_sound(*args, **kwargs):
#     PlaySound()
#
#
# sound_manager = ThreadManager(run_sound)
# mqtt_status_manage_thread_factory(device_id, 'speaker', mqtt_client, sound_manager)

mqtt_client.client.loop_forever()
