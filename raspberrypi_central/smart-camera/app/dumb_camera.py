import os

from service_manager.run_dumb_camera import RunDumbCamera
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from thread.thread_manager import ThreadManager
from mqtt.mqtt_client import get_mqtt

device_id = os.environ['DEVICE_ID']

camera_mqtt_client = get_mqtt(f"{device_id}-dumb-camera")

camera_manager = ThreadManager(RunDumbCamera())

mqtt_status_manage_thread_factory(device_id, 'camera', camera_mqtt_client, camera_manager, status_json=True)

camera_mqtt_client.client.loop_forever()
