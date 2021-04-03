import io
import time

from picamera import PiCamera
import os

import logging

LOGGER = logging.getLogger(__name__)

class PiVideoStream:

    BASE_VIDEO_PATH = os.environ['MEDIA_FOLDER']

    def __init__(self, process_frame, resolution, framerate, **kwargs):
        self.process_frame = process_frame
        self.resolution = resolution
        self.framerate = framerate
        self.kwargs = kwargs

        self.camera = None
        self._record = False
        self._framerate_before_record = self.framerate

    def run(self):
        self.camera = PiCamera()
        # Camera warm-up time
        time.sleep(2)

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

    def start_recording(self, video_ref: str) -> None:
        if self._record is False:
            LOGGER.info(f'start recording video_ref={video_ref}')

            self._framerate_before_record = self.camera.framerate
            self.high_fps()

            self._record = True

            self.camera.start_recording(os.path.join(PiVideoStream.BASE_VIDEO_PATH, f'{video_ref}.h264'))

    def stop_recording(self) -> None:
        if self._record is True:
            LOGGER.info(f'stop recording, change frame rate to {self._framerate_before_record}')
            self.camera.stop_recording()
            self._record = False

            self.camera.framerate = self._framerate_before_record

    def split_recording(self, video_ref: str) -> None:
        if self._record is True:
            LOGGER.info(f'split_recording video_ref={video_ref}')

            # Continue the recording in the specified output; close existing output.
            self.camera.split_recording(os.path.join(PiVideoStream.BASE_VIDEO_PATH, f'{video_ref}.h264'))

    def high_fps(self):
        if self._record is False:
            LOGGER.info('change camera framerate for 25 (high)')
            self.camera.framerate = 25

    def low_fps(self):
        if self._record is False:
            LOGGER.info('change camera framerate for 1 (low)')
            self.camera.framerate = 1
