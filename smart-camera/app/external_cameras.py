import os
from mqtt.mqtt_manage_runnable import MqttManageRunnable
from service_manager.run_camera_frame_producer import RunCameraFrameProducer
from mqtt.mqtt_client import get_mqtt


device_id = os.environ['DEVICE_ID']

camera_mqtt_client = get_mqtt(f"{device_id}-external-camera_manager")

camera_manager = RunCameraFrameProducer()
MqttManageRunnable(device_id, 'camera_manager', camera_mqtt_client, camera_manager, multi_device=True, status_json=True)

camera_mqtt_client.client.loop_forever()
