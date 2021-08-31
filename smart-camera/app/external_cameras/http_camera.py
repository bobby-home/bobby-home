from external_cameras.data import HTTPCameraData
import sched, time, io
import requests
import logging
from camera.camera_frame_producer import CameraFrameProducer


logger = logging.getLogger(__name__)


class HttpCamera:
    """Integrate HTTP Camera to Bobby. Should have an url to request a frame.
    This class will retrieve frames from http when it should to send them to Bobby.
    Thanks to this, you could integrate any camera that expose an http endpoint to request a frame.
    """
    def __init__(self, http_camera_data: HTTPCameraData, sender: CameraFrameProducer) -> None:
        self._http_camera_data = http_camera_data
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._sender = sender
        self._stop = False
        self._scheduler.enter(1, 1, self._send)
        self._scheduler.run()

    def stop(self) -> None:
        self._stop = True

    def _send(self) -> None:
        try:
            response = requests.get(
                self._http_camera_data.endpoint,
                auth=(self._http_camera_data.user, self._http_camera_data.password)
            )
        except requests.exceptions.RequestException:
            logger.error("Request to get frame failed.", exc_info=True)
        else:
            data = response.content
            try:
                frame = io.BytesIO(data)
            except TypeError:
                logger.error("Data from {self._http_camera_data.endpoint} cannot be converted to Python BytesIO.", exc_info=True)
            else:
                self._sender.process_frame(frame, stream=False, process=True)

        # Even if an exception got caught we need to schedule the next run.
        if not self._stop:
            self._scheduler.enter(1, 1, self._send)
