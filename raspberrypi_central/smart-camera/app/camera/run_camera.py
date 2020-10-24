from typing import List, Optional

from camera.camera import Camera
from camera.camera_analyze import Consideration, CameraAnalyzeObject
from camera.camera_factory import camera_factory
from camera.videostream import VideoStream
from camera_analyze.all_analyzer import NoAnalyzer
from camera_analyze.roi_analyzer import IsConsideredByAnyAnalyzer, ROICamera
from mqtt.mqtt_client import get_mqtt_client
from roi.roi import RectangleROI
from service_manager.service_manager import RunService


def roi_camera_from_args(args) -> Optional[CameraAnalyzeObject]:
    """
    {"status": true, "data": [{"id": 1, "x": 128.0, "y": 185.0, "w": 81.0, "h": 76.0, "definition_width": 300.0, "definition_height": 300.0, "device_id": 1}, {"id": 2, "x": 50.0, "y": 50.0, "w": 50.0, "h": 50.0, "definition_width": 300.0, "definition_height": 300.0, "device_id": 1}]}
    I have to manage to have multiple CameraAnalyzeObject
    or... I might use another class to handle multiple camera analyze object,
    so I could do stuff like, if in CameraRectangleROI and it is not someone that I know (facial recognition), then we consider the people
    -> ring the alarm.
    """

    # if args is empty, we will have: ([],)
    if args and len(args) > 1:
        args = args[0]

        analyzers: List[CameraAnalyzeObject] = []

        for rectangle in args:
            consideration = Consideration(id=rectangle['id'], type='rectangle')

            rectangle_roi = RectangleROI(consideration=consideration, x=rectangle['x'], y=rectangle['y'], w=rectangle['w'], h=rectangle['h'],
                                         definition_width=rectangle['definition_width'],
                                         definition_height=rectangle['definition_height'])
            analyzer = ROICamera(rectangle_roi)
            analyzers.append(analyzer)

        return IsConsideredByAnyAnalyzer(analyzers)

    return None


class RunSmartCamera(RunService):

    def __init__(self):
        self._stream = None
        self._camera = None
        self._camera_analyze_object = None

    def prepare_run(self, *args):
        self._camera_analyze_object = roi_camera_from_args(args)

        if self._camera_analyze_object is None:
            # No analyzer, every people will be considered
            consideration = Consideration(type='all')
            self._camera_analyze_object = NoAnalyzer(consideration)

        self._camera = camera_factory(get_mqtt_client, self._camera_analyze_object)

    def run(self) -> None:
        camera_width = 640
        camera_height = 480

        self._camera.start()

        # TODO: see issue #78
        self._stream = VideoStream(self._camera.process_frame, resolution=(
            camera_width, camera_height), framerate=1, pi_camera=False)

    def is_restart_necessary(self, *args) -> bool:
        new_roi = roi_camera_from_args(args)
        return new_roi != self._camera_analyze_object

    def stop(self, *args) -> None:
        pass
