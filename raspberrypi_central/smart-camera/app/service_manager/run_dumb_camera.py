import os
from io import BytesIO

from camera.camera_config import camera_config
from camera.dumb_camera import DumbCamera
from camera.pivideostream import PiVideoStream
from service_manager.service_manager import RunService
from utils.rate_limit import rate_limited

CAMERA_WIDTH = camera_config.camera_width
CAMERA_HEIGHT = camera_config.camera_height


class RunDumbCamera(RunService):

    def __init__(self):
        pass

    def prepare_run(self, data = None) -> None:
        pass

    def run(self) -> None:
        print('run dumb camera!')
        camera = DumbCamera(os.environ['DEVICE_ID'])

        @rate_limited(max_per_second=1, thread_safe=False, block=False)
        def process_frame(frame: BytesIO):
            print('process frame bridge with rate limit')
            camera.process_frame(frame)

        stream = PiVideoStream(process_frame, resolution=(
            CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30)

        stream.run()
        # unreachable code because .run() contains an endless loop.

    def is_restart_necessary(self, data = None) -> bool:
        """
        Light camera is dumb, stateless so it does not need to restart to apply configuration changes.
        """
        return False

    def __str__(self):
        return 'run-dumb-camera'
