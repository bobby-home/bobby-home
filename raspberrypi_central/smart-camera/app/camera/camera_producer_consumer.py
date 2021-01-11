import io
import multiprocessing as mp
from queue import Empty, Full

from utils.rate_limit import rate_limited


class FrameProducer:
    def __init__(self, queues, camera_record_event: mp.Event, camera_record_queue: mp.Queue):
        self.queues = queues
        self.camera_record_queue = camera_record_queue
        self.camera_record_event = camera_record_event
        self.camera_stream = None

    def set_camera_steam(self, camera_stream):
        self.camera_stream = camera_stream

    def _manage_record(self):
        try:
            record_event_ref = self.camera_record_queue.get_nowait()
        except Empty:
            pass
        else:
            self.camera_stream.start_recording(record_event_ref)

        if not self.camera_record_event.is_set():
            self.camera_stream.stop_recording()

    def produce(self, raw_capture):
        self._manage_record()

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
