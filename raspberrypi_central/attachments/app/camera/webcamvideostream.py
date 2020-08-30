from threading import Thread
import cv2


class WebcamVideoStream:
    def __init__(self, processFrame, resolution, framerate, src=0):
        self.processFrame = processFrame

        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FPS, framerate)

        (width, height) = resolution
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # read the first frame from the stream
        _ = self.stream.read()
        self._update()


    def _update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            (_, frame) = self.stream.read()
            self.processFrame(frame)

