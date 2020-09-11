from picamera.array import PiRGBArray
from picamera import PiCamera


class PiVideoStream:
    def __init__(self, processFrame, resolution, framerate, **kwargs):
        self.processFrame = processFrame

        self.camera = PiCamera()

        # set camera parameters
        self.camera.resolution = resolution
        self.camera.framerate = framerate

        # set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in kwargs.items():
            setattr(self.camera, arg, value)

        # initialize the stream
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format='jpeg', use_video_port=True)

        self._update()

    def _update(self):
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            frame = f.array
            self.processFrame(frame)
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            frame = f.array
            self.processFrame(frame)
            self.rawCapture.truncate(0)

# if self.stopped:
# 	self.stream.close()
# 	self.rawCapture.close()
# 	self.camera.close()
# 	return
