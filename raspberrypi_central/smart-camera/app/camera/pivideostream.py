import io
import time

from picamera.array import PiRGBArray
from picamera import PiCamera


class PiVideoStream:
    def __init__(self, process_frame, resolution, framerate, **kwargs):
        self.process_frame = process_frame
        self.resolution = resolution
        self.framerate = framerate
        self.kwargs = kwargs

        self.camera = None
        self._record = False

    def run(self):
        self.camera = PiCamera()

        camera = self.camera

        camera.resolution = self.resolution
        camera.framerate = self.framerate

        # set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in self.kwargs.items():
            setattr(camera, arg, value)

        raw_capture = io.BytesIO()
        for _ in camera.capture_continuous(raw_capture, format='jpeg', use_video_port=True):
            raw_capture.seek(0)

            self.process_frame(raw_capture)

            # "Rewind" the stream to the beginning so we can read its content
            raw_capture.seek(0)
            raw_capture.truncate()

    def start_recording(self, video_ref):
        if self._record is False:
            print('start record')
            self._record = True
            self.camera.start_recording(f'videos/{video_ref}.h264')

    def stop_recording(self):
        if self._record is True:
            print('stop record')
            self.camera.stop_recording()
            self._record = False
