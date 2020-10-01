import os
from typing import Optional

from camera.camera_analyze import CameraAnalyzeObject
from roi.roi import RectangleROI
from camera_analyze.all_analyzer import NoAnalyzer
from camera_analyze.roi_analyzer import ROICamera
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from service_manager.service_manager import RunService
from thread.thread_manager import ThreadManager
from camera.camera_factory import camera_factory
from mqtt.mqtt_client import get_mqtt_client
from camera.videostream import VideoStream


device_id = os.environ['DEVICE_ID']

mqtt_client = get_mqtt_client(f"{device_id}-rpi4-alarm-motion")


def roi_camera_from_args(args) -> Optional[CameraAnalyzeObject]:
    if args and len(args) > 0:
        args = args[0]
        rectangle_roi = RectangleROI(x=args['x'], y=args['y'], w=args['w'], h=args['h'],
                                     definition_width=args['definition_width'], definition_height=args['definition_height'])
        return ROICamera(rectangle_roi)

    return None


class RunSmartCamera(RunService):

    def __init__(self):
        self._stream = None
        self._camera = None
        self._camera_roi = None
        pass

    def prepare_run(self, *args):
        self._camera_roi = roi_camera_from_args(args)
        if self._camera_roi is None:
            self._camera_roi = NoAnalyzer()

        self._camera = camera_factory(get_mqtt_client, self._camera_roi)

    def run(self) -> None:
        camera_width = 640
        camera_height = 480

        # TODO: see issue #78
        self._stream = VideoStream(self._camera.process_frame, resolution=(
            camera_width, camera_height), framerate=1, pi_camera=False)

    def is_restart_necessary(self, *args) -> bool:
        new_roi = roi_camera_from_args(args)
        return new_roi != self._camera_roi

    def stop(self, *args) -> None:
        pass


manager = ThreadManager(RunSmartCamera())
mqtt_status_manage_thread_factory(device_id, 'camera', mqtt_client, manager, status_json=True)


# def run_sound(*args, **kwargs):
#     PlaySound()
#
#
# sound_manager = ThreadManager(run_sound)
# mqtt_status_manage_thread_factory(device_id, 'speaker', mqtt_client, sound_manager)

mqtt_client.loop_forever()
