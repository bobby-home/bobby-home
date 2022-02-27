import os
import threading
import signal
from functools import partial
from io import BytesIO
from typing import Dict
from multiprocessing import Process
import logging

from camera.camera_config import camera_config
from camera.manage_record import camera_record_factory
from camera.camera_frame_producer import CameraFrameProducer
from camera.pivideostream import PiVideoStream
from service_manager.runnable import Runnable
import multiprocessing as mp
CAMERA_WIDTH = camera_config.camera_width
CAMERA_HEIGHT = camera_config.camera_height

DEVICE_ID = os.environ['DEVICE_ID']
LOGGER = logging.getLogger(__name__)


class FrameProducer:
    def __init__(self, stream_event: mp.Event, process_event: mp.Event):
        self._stream_event = stream_event
        self._process_event = process_event

    def run(self, device_id: str) -> None:
        LOGGER.info('run camera frame producer')
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
            camera.process_frame(frame, stream=self._stream_event.is_set(), process=self._process_event.is_set())

        stream.process_frame = process_frame

        camera_record_factory(DEVICE_ID, stream)
        stream.run()

class RunCameraFrameProducer(Runnable):
    def __init__(self):
        self._stream_event = mp.Event()
        self._process_event = mp.Event()

        self._frame_producer = FrameProducer(self._stream_event, self._process_event)
        self._process = None

    def _process_join(self, process) -> None:
        process.join()

        if process.exitcode != -signal.SIGTERM:
            # something went wrong in the child process
            # -> kill the process. Remainder: we are inside a thread here,
            # so it appears that sys.exit(1) does not work... So, we will!
            os.kill(os.getpid(), signal.SIGINT)

    def run(self, device_id: str, status: bool, data=None) -> None:
        """
        Be careful to Falsy value! None does not mean to turn off the stream/process
        i.e data={'to_analyze': None, 'stream': False}
        do a strict equal to turn on/off something.
        """

        if data:
            if 'stream' in data:
                if data['stream'] is True:
                    self._stream_event.set()
                elif data['stream'] is False:
                    self._stream_event.clear()

            if 'to_analyze' in data:
                if data['to_analyze'] is True:
                    self._process_event.set()
                elif data['to_analyze'] is False:
                    self._process_event.clear()

        if status is True and self._process is None:
            run = partial(self._frame_producer.run, device_id)
            self._process = Process(target=run, daemon=True)

            verify = partial(self._process_join, self._process)
            t = threading.Thread(target=verify, daemon=True)

            self._process.start()
            t.start()

            return

        if status is False and self._process:
            self._process.terminate()
            self._process = None

    def __str__(self):
        return 'run-camera-frame-producer'
