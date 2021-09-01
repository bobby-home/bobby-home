import os
from service_manager.run_external_cameras import ConnectedDevices, RunHTTPExternalCameras
from mqtt.mqtt_manage_runnable import MqttManageRunnable
from mqtt.mqtt_client import get_mqtt


device_id = os.environ['DEVICE_ID']

mqtt_client = get_mqtt(f"{device_id}-external-camera_manager")

manager = RunHTTPExternalCameras(ConnectedDevices())
MqttManageRunnable(device_id, 'camera_manager', mqtt_client, manager, multi_device=True, status_json=True)

mqtt_client.client.loop_forever()
