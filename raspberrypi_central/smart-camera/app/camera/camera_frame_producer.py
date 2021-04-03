from io import BytesIO
from mqtt.mqtt_client import get_mqtt
from utils.rate_limit import rate_limited




class CameraFrameProducer:
    """Take frames from picamera and send it through mqtt to be processed.
    """
    SERVICE_NAME = 'dumb_camera'
    TOPIC_PICTURE_TO_ANALYZE = 'ia/picture'

    TOPIC_PICTURE_STREAM = 'camera/stream'

    def __init__(self, device_id: str):
        self._device_id = device_id
        self.mqtt_client = None
        self.start()

    @rate_limited(max_per_second=0.5, block=False)
    def publish_to_analyze(self, picture):
        self.mqtt_client.publish(f'{self.TOPIC_PICTURE_TO_ANALYZE}/{self._device_id}', picture, qos=0)

    def start(self) -> None:
        mqtt_client = get_mqtt(client_name=f'{self._device_id}-{CameraFrameProducer.SERVICE_NAME}')
        mqtt_client.connect_keep_status(CameraFrameProducer.SERVICE_NAME, self._device_id)
        self.mqtt_client = mqtt_client.client

        # <!> without this, the process send some pictures (~19) and then nothing... So it is mandatory!
        self.mqtt_client.loop_start()

    def process_frame(self, frame: BytesIO, stream: bool, process: bool):
        picture = frame.getvalue()

        if process is True:
            self.publish_to_analyze(picture)

        if stream is True:
            self.mqtt_client.publish(f'{self.TOPIC_PICTURE_STREAM}/{self._device_id}', picture, qos=0)
