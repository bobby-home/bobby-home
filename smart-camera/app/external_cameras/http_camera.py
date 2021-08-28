from external_cameras.data import HTTPCameraData
import sched, time, io
import requests
from camera.camera_frame_producer import CameraFrameProducer


class HttpCamera:
    """Integrate HTTP Camera to Bobby. Should have an url to request a frame.
    This class will retrieve frames from http when it should to send them to Bobby.
    Thanks to this, you could integrate any camera that expose an http endpoint to request a frame.
    """
    def __init__(self, http_camera_data: HTTPCameraData, sender: CameraFrameProducer) -> None:
        self._http_camera_data = http_camera_data
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._sender = sender

        self._scheduler.enter(1, 1, self._send)
        self._scheduler.run()

    def _send(self):
        data = requests.get(
            self._http_camera_data.endpoint,
            auth=(self._http_camera_data.user, self._http_camera_data.password)
        ).content

        frame = io.BytesIO(data)

        self._sender.process_frame(frame, stream=False, process=True)
        self._scheduler.enter(1, 1, self._send)
