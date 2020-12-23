import io

from picamera.array import PiRGBArray
from picamera import PiCamera


class PiVideoStream:
    def __init__(self, process_frame, resolution, framerate, **kwargs):
        self.process_frame = process_frame
        self.resolution = resolution
        self.framerate = framerate
        self.kwargs = kwargs

        self._run()

    def _run(self):
       with PiCamera() as camera:
            camera.resolution = self.resolution
            camera.framerate = self.framerate

            # set optional camera parameters (refer to PiCamera docs)
            for (arg, value) in self.kwargs.items():
                setattr(camera, arg, value)

            rawCapture = io.BytesIO()
            for _ in camera.capture_continuous(rawCapture, format='jpeg'):
                rawCapture.seek(0)

                self.process_frame(rawCapture)

                # "Rewind" the stream to the beginning so we can read its content
                rawCapture.seek(0)
                rawCapture.truncate()
