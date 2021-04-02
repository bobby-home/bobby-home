import logging
import os
import traceback
from service_manager.run_camera_frame_producer import RunCameraFrameProducer

logger = logging.getLogger('dumb_camera')
DEVICE_ID = os.environ['DEVICE_ID']


class RunDumbCameraFrameProducer(RunCameraFrameProducer):

    def run(self) -> None:
        try:
            super().run()
        except BaseException as e:
            tags = {'device': DEVICE_ID}
            logger.error(traceback.format_exc(),
                         extra={'tags': tags})

            raise

    def __str__(self):
        return 'run-dumb-camera-frame-producer'
