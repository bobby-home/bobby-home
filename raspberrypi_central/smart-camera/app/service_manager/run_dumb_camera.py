import os
from io import BytesIO

from mqtt.mqtt_client import get_mqtt
from camera.camera_config import camera_config
from camera.dumb_camera import DumbCamera
from camera.pivideostream import PiVideoStream
from service_manager.service_manager import RunService
from utils.rate_limit import rate_limited
from camera.camera_record import DumbCameraRecord


CAMERA_WIDTH = camera_config.camera_width
CAMERA_HEIGHT = camera_config.camera_height

DEVICE_ID = os.environ['DEVICE_ID']

class ManageRecord():
    def __init__(self, video_stream: PiVideoStream) -> None:
        self._video_stream = video_stream

        self._mqtt_client = get_mqtt(f'{DEVICE_ID}-manage-record')
        self._mqtt_client.connect()
        self._mqtt_client.client.loop_start()

        self._setup_listeners()

    def _extract_data_from_topic(self, topic: str) -> None:
        split = topic.split('/')

        data = {
            'action': split[3],
        }

        if len(split) > 3:
            data['video_ref'] = split[4]

        return data

    def _on_record(self, client, userdata, message) -> None:
        data = self._extract_data_from_topic(message.topic)

        if data['action'] == 'start':
            self._video_stream.start_recording(data['video_ref'])
        elif data['action'] == 'split':
            self._video_stream.split_recording(data['video_ref'])
        elif data['action'] == 'end':
            self._video_stream.stop_recording()

    def _setup_listeners(self) -> None:
        self._mqtt_client.client.subscribe(f'camera/recording/{DEVICE_ID}/#', qos=1)
        self._mqtt_client.client.message_callback_add(f'camera/recording/{DEVICE_ID}/', self._on_record)

class RunDumbCamera(RunService):

    def __init__(self):
        pass

    def is_restart_necessary(self, data = None) -> bool:
        """
        Dumb camera is stateless so it does not need to restart to apply configuration changes.
        """
        return False

    def prepare_run(self, data = None) -> None:
        """
        Dumb camera is stateless so it does not need to prepare any data to run.
        """
        pass

    def run(self) -> None:
        print('run dumb camera!')
        camera = DumbCamera(os.environ['DEVICE_ID'])

        @rate_limited(max_per_second=1, thread_safe=False, block=False)
        def process_frame(frame: BytesIO):
            print('process frame bridge with rate limit')
            camera.process_frame(frame)

        stream = PiVideoStream(process_frame, resolution=(
            CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30)

        ManageRecord(stream)

        stream.run()
        # unreachable code because .run() contains an endless loop.


    def __str__(self):
        return 'run-dumb-camera'
