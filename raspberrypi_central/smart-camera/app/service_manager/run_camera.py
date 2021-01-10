import io
import signal
from typing import Callable

from camera.camera import Camera
from camera.camera_config import camera_config
from camera.camera_record import CameraRecord

from camera.camera_factory import camera_factory
from camera.videostream import video_stream_factory
from mqtt.mqtt_client import get_mqtt_client
from service_manager.roi_camera_from_args import roi_camera_from_args
from service_manager.service_manager import RunService

from queue import Full, Empty
import multiprocessing as mp

from utils.rate_limit import rate_limited

CAMERA_WIDTH = camera_config.camera_width
CAMERA_HEIGHT = camera_config.camera_height


class RunSmartCamera(RunService):

    def __init__(self, camera_factory: Callable[[], Camera], video_stream):
        self._stream = None
        self._camera = None
        self._camera_analyze_object = None
        self.camera_factory = camera_factory
        self.video_stream = video_stream

        self.capture_proc = None
        self.consumer_proc = None

    def prepare_run(self, data = None) -> None:
        self._camera_analyze_object = roi_camera_from_args(data)

        self._camera = self.camera_factory(get_mqtt_client, self._camera_analyze_object)

    def _exit_gracefully(self, signum, frame):
        self.capture_proc.terminate()
        self.consumer_proc.terminate()

    def run(self) -> None:
        queue = mp.Queue(maxsize=10)

        # we process one frame at the time. If we loose some frames to analyze it is not an issue.
        queue_model = mp.Queue(maxsize=1)

        camera_record_event = mp.Event()
        camera_record_queue = mp.Queue(maxsize=1)

        frame_producer = FrameProducer([queue, queue_model], camera_record_event, camera_record_queue)
        camera_consumer = FrameIAConsumer(self._camera)

        camera_record = CameraRecord(camera_record_event, camera_record_queue)
        self._camera.camera_recorder = camera_record

        # TODO: see issue #78
        self._stream = self.video_stream(frame_producer.produce, resolution=(
            CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30, pi_camera=True)

        frame_producer.set_camera_steam(self._stream)

        capture_proc = mp.Process(target=self._stream.run)
        consumer_proc = mp.Process(target=camera_consumer.process_frame, args=(queue_model,))

        consumer_proc.start()
        capture_proc.start()

        self.capture_proc = capture_proc
        self.consumer_proc = consumer_proc

        signals = [
            signal.SIGINT,
            signal.SIGTERM,
            # this signal produces an error: OSError: [Errno 22] Invalid argument
            # or just make the signal doesn't work with a for loop.
            # signal.SIGKILL,
        ]

        # warning: signal handler should be after we assign processes to self.
        for signum in signals:
            signal.signal(signum, self._exit_gracefully)

    def is_restart_necessary(self, data = None) -> bool:
        new_roi = roi_camera_from_args(data)
        return new_roi != self._camera_analyze_object

    def stop(self, *args) -> None:
        pass

    def __str__(self):
        return 'run-smart-camera'


class FrameProducer:
    def __init__(self, queues, camera_record_event: mp.Event, camera_record_queue: mp.Queue):
        self.queues = queues
        self.camera_record_queue = camera_record_queue
        self.camera_record_event = camera_record_event
        self.camera_stream = None

    def set_camera_steam(self, camera_stream):
        self.camera_stream = camera_stream

    def manage_record(self):

        try:
            record_event_ref = self.camera_record_queue.get_nowait()
        except Empty:
            pass
        else:
            self.camera_stream.start_recording(record_event_ref)

        if not self.camera_record_event.is_set():
            self.camera_stream.stop_recording()

    def produce(self, raw_capture):
        self.manage_record()

        # get bytes from BytesIO, image is bytes here.
        image_bytes = raw_capture.read()

        for queue in self.queues:
            try:
                queue.put(image_bytes, False)
            except Full:
                # if the Queue is full, then we ignore frames.
                pass


class FrameIAConsumer:
    """
    Take frames from queue and send it to process.
    """
    def __init__(self, camera):
        self.camera = camera

    def process_frame(self, queue):
        # start mqtt connection
        self.camera.start()

        # we don't need to be thread safe because we don't use threads.
        @rate_limited(1, thread_safe=False)
        def process_frame():
            try:
                stream = io.BytesIO(queue.get_nowait())
            except Empty:
                pass
            else:
                self.camera.process_frame(stream)

        while True:
            process_frame()


def run_smart_camera_factory():
    return RunSmartCamera(camera_factory, video_stream_factory)
