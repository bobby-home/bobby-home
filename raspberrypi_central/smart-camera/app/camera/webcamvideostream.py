import io

import cv2


class WebcamVideoStream:
    def __init__(self, process_frame, resolution, framerate, src=0):
        self.process_frame = process_frame

        self.stream = cv2.VideoCapture(src)

        # https://stackoverflow.com/questions/48049886/how-to-correctly-check-if-a-camera-is-available
        if self.stream is None or not self.stream.isOpened():
            raise Exception(f'Unable to open video source {src} with OpenCV.')

        self.stream.set(cv2.CAP_PROP_FPS, framerate)

        (width, height) = resolution
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # read the first frame from the stream
        _ = self.stream.read()
        self._update()

    def __del__(self):
        self.stream.release()

    def _update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            (_, frame) = self.stream.read()

            # Some frames could be None at the beginning.
            if frame is None:
                continue

            is_success, im_buf_arr = cv2.imencode(".jpg", frame)
            io_buf = io.BytesIO(im_buf_arr)

            self.process_frame(io_buf)
