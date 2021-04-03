import os
from functools import partial
from io import BytesIO
from typing import Dict
from multiprocessing import Process

from mqtt.mqtt_client import get_mqtt
from camera.camera_config import camera_config
from camera.camera_frame_producer import CameraFrameProducer
from camera.pivideostream import PiVideoStream
from service_manager.runnable import Runnable
from service_manager.service_manager import RunService
from utils.rate_limit import rate_limited
import multiprocessing as mp
CAMERA_WIDTH = camera_config.camera_width
CAMERA_HEIGHT = camera_config.camera_height
from queue import Empty
DEVICE_ID = os.environ['DEVICE_ID']

class ManageRecord:
    """
    Manage record through MQTT for dumb camera.
    It receives MQTT messages, process it to manage records.
    """
    def __init__(self, video_stream: PiVideoStream) -> None:
        self._video_stream = video_stream

        self._mqtt_client = get_mqtt(f'{DEVICE_ID}-manage-record')
        self._mqtt_client.connect()
        self._mqtt_client.client.loop_start()

        self._setup_listeners()

    @staticmethod
    def _extract_data_from_topic(topic: str) -> Dict[str, str]:
        split = topic.split('/')

        data = {
            'action': split[3],
        }

        if len(split) > 4:
            data['video_ref'] = split[4]

        return data

    def _on_record(self, _client, _userdata, message) -> None:
        data = self._extract_data_from_topic(message.topic)
        print(f'dumb_camera: on_record {data}')

        if data['action'] == 'start':
            self._video_stream.start_recording(data['video_ref'])
        elif data['action'] == 'split':
            self._video_stream.split_recording(data['video_ref'])
        elif data['action'] == 'end':
            self._video_stream.stop_recording()

    def _setup_listeners(self) -> None:
        self._mqtt_client.client.subscribe(f'camera/recording/{DEVICE_ID}/#', qos=2)
        self._mqtt_client.client.message_callback_add(f'camera/recording/{DEVICE_ID}/#', self._on_record)

class FrameProducer:
    def __init__(self, stream_event: mp.Event, process_event: mp.Event, high_fps_queue: mp.Queue):
        self._high_fps_queue = high_fps_queue
        self._stream_event = stream_event
        self._process_event = process_event

    def run(self, device_id: str) -> None:
        print('run camera frame producer!')
        camera = CameraFrameProducer(device_id)

        stream = PiVideoStream(None, resolution=(
            CAMERA_WIDTH, CAMERA_HEIGHT), framerate=25)

        """
        For fps processing, we do not change directly FPS because we need to record at high fps.
        If the camera is recording and we try to change the camera fps we get this error:
            raise PiCameraRuntimeError("Recording is currently running")
        """

        # @rate_limited(max_per_second=0.5, thread_safe=False, block=True)
        def process_frame(frame: BytesIO):
            try:
                high_fps = self._high_fps_queue.get(block=False)
            except Empty:
                # it does not need to change fps
                high_fps = None

            if high_fps is not None:
                stream.high_fps() if high_fps is True else stream.low_fps()

            camera.process_frame(frame, stream=self._stream_event.is_set(), process=self._process_event.is_set())

        stream.process_frame = process_frame

        ManageRecord(stream)
        stream.run()

class RunCameraFrameProducer(Runnable):
    def __init__(self):
        self._high_fps_queue = mp.Queue()
        self._stream_event = mp.Event()
        self._process_event = mp.Event()

        self._frame_producer = FrameProducer(self._stream_event, self._process_event, self._high_fps_queue)
        self._process = None

    def run(self, device_id: str, status: bool, data=None) -> None:
        print(f'run camera frame producer status={status} data={data}')

        if data:
            if 'stream' in data:
                if data['stream'] is True:
                    self._high_fps_queue.put(True)
                    self._stream_event.set()
                else:
                    self._stream_event.clear()
                    self._high_fps_queue.put(False)

            if 'to_analyze' in data:
                if data['to_analyze'] is True:
                    self._process_event.set()
                else:
                    self._process_event.clear()

        if status is True and self._process is None:
            run = partial(self._frame_producer.run, device_id)
            self._process = Process(target=run)
            self._process.start()
            return

        if status is False and self._process:
            self._process.terminate()
            self._process = None

    def __str__(self):
        return 'run-camera-frame-producer'
