import os

from service_manager.run_camera import run_smart_camera_factory
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from thread.thread_manager import ThreadManager
from mqtt.mqtt_client import get_mqtt

device_id = os.environ['DEVICE_ID']

camera_mqtt_client = get_mqtt(f"{device_id}-camera-manager")

camera_manager = ThreadManager(run_smart_camera_factory())
mqtt_status_manage_thread_factory(device_id, 'camera', camera_mqtt_client, camera_manager, status_json=True)

camera_mqtt_client.client.loop_forever()
