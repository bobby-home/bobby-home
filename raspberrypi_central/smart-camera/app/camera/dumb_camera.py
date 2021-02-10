from io import BytesIO
from mqtt.mqtt_client import get_mqtt


class DumbCamera:
    """Runs on little end device. Take frames from picamera and send it through mqtt.
    """
    SERVICE_NAME = 'dumb_camera'
    PICTURE_TOPIC = 'ia/picture'

    def __init__(self, device_id: str):
        self._device_id = device_id
        self.mqtt_client = None
        self.start()

    def start(self) -> None:
        mqtt_client = get_mqtt(client_name=f'{self._device_id}-{DumbCamera.SERVICE_NAME}')
        mqtt_client.connect_keep_status(DumbCamera.SERVICE_NAME, self._device_id)
        self.mqtt_client = mqtt_client.client

        # <!> without this, the process send some pictures (~19) and then nothing... So it is mandatory!
        self.mqtt_client.loop_start()

    def process_frame(self, frame: BytesIO):
        picture = frame.getvalue()

        self.mqtt_client.publish(f'{self.PICTURE_TOPIC}/{self._device_id}', picture, qos=1)
