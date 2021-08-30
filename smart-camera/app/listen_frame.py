import io
import os
import logging

from camera.camera_frame_producer import CameraFrameProducer
from mqtt.mqtt_client import get_mqtt
from mqtt.mqtt_manage_runnable import MqttManageRunnable
from service_manager.run_listen_frame import RunListenFrame, ConnectedDevices


logger = logging.getLogger(__name__)

def extract_data_from_topic(topic: str):
    split = topic.split('/')

    return {
        'device_id': split[2]
    }


DEVICE_ID = os.environ['DEVICE_ID']

class FrameReceiver:
    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def on_picture(self, _client, _userdata, message):
        data = extract_data_from_topic(message.topic)
        from_device_id = data['device_id']

        camera = self._connected_devices.connected_devices.get(from_device_id, None)

        if camera:
            try:
                image = io.BytesIO(message.payload)
            except TypeError:
                logger.critical("Cannot convert received payload to BytesIO. Actual type: %s", type(message.payload))
                return

            camera.process_frame(image)

mqtt_client = get_mqtt(f'{DEVICE_ID}-analyzer')


connected_devices = ConnectedDevices(mqtt_client)
frame_receiver = FrameReceiver(connected_devices)

def subscribe(client) -> None:
    # topics to receive frames to analyze for dumb cameras.
    client.subscribe(f'{CameraFrameProducer.TOPIC_PICTURE_TO_ANALYZE}/+', qos=0)
    client.message_callback_add(f'{CameraFrameProducer.TOPIC_PICTURE_TO_ANALYZE}/+', frame_receiver.on_picture)

mqtt_client.on_connected_callbacks.append(subscribe)
mqtt_client.connect()

# topics to know when a camera is up/off
camera_manager = RunListenFrame(connected_devices)
MqttManageRunnable(DEVICE_ID, 'object_detection_manager', get_mqtt(f'{DEVICE_ID}-object_detection_manager'), camera_manager, status_json=True, multi_device=True)

mqtt_client.client.loop_forever()
