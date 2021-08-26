import sched, time, io
import requests
from camera.camera_frame_producer import CameraFrameProducer


class HttpCamera:
    """Integrate HTTP Camera to Bobby. Should have an url to request a frame.
    This class will retrieve frames from http when it should to send them to Bobby.
    Thanks to this, you could integrate any camera that expose an http endpoint to request a frame.
    """
    def __init__(self, url: str, sender: CameraFrameProducer) -> None:
        self._url = url
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._sender = sender

        self._scheduler.enter(1, 1, self._send)
        self._scheduler.run()

    def _send(self):
        # todo: auth!
        data = requests.get(self._url, auth=('mx', 'coucou')).content
        frame = io.BytesIO(data)

        self._sender.process_frame(frame, stream=False, process=True)
        self._scheduler.enter(1, 1, self._send)

