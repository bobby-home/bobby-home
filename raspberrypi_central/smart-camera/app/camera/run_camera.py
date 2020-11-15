from typing import List, Callable

from camera.camera import Camera
from camera_analyze.camera_analyzer import Consideration, CameraAnalyzer
from camera.camera_factory import camera_factory
from camera.videostream import VideoStream
from camera_analyze.all_analyzer import NoAnalyzer
from camera_analyze.roi_analyzer import ROICameraAnalyzer
from camera_analyze.considered_by_any_analyzer import ConsideredByAnyAnalyzer
from mqtt.mqtt_client import get_mqtt_client
from roi.roi import RectangleROI
from service_manager.service_manager import RunService


def roi_camera_from_args(data = None) -> CameraAnalyzer:
    """
    {"status": true, "data": [{"id": 1, "x": 128.0, "y": 185.0, "w": 81.0, "h": 76.0, "definition_width": 300.0, "definition_height": 300.0, "device_id": 1}, {"id": 2, "x": 50.0, "y": 50.0, "w": 50.0, "h": 50.0, "definition_width": 300.0, "definition_height": 300.0, "device_id": 1}]}
    I have to manage to have multiple CameraAnalyzeObject
    or... I might use another class to handle multiple camera analyze object,
    so I could do stuff like, if in CameraRectangleROI and it is not someone that I know (facial recognition), then we consider the people
    -> ring the alarm.
    """

    rois = data.get('rois', None)

    analyzers: List[CameraAnalyzer] = []

    if rois:
        if 'rectangles' in rois:
            rectangles = rois.get('rectangles')
            for rectangle in rectangles:
                consideration = Consideration(id=rectangle['id'], type='rectangles')

                rectangle_roi = RectangleROI(consideration=consideration, x=rectangle['x'], y=rectangle['y'],
                                             w=rectangle['w'], h=rectangle['h'],
                                             definition_width=rois['definition_width'],
                                             definition_height=rois['definition_height'])

                analyzer = ROICameraAnalyzer(rectangle_roi)
                analyzers.append(analyzer)

            return ConsideredByAnyAnalyzer(analyzers)

        if 'full' in rois:
            consideration = Consideration(type='full')
            return NoAnalyzer(consideration)

        raise ValueError(f"Can't find any supported rois in {rois}.")
    else:
        raise ValueError(f"Can't find the key 'rois' in {data}")


class RunSmartCamera(RunService):

    def __init__(self, camera_factory: Callable[[], Camera], video_stream: Callable[[any], VideoStream]):
        self._stream = None
        self._camera = None
        self._camera_analyze_object = None
        self.camera_factory = camera_factory
        self.video_stream = video_stream

    def prepare_run(self, data = None) -> None:
        self._camera_analyze_object = roi_camera_from_args(data)

        self._camera = self.camera_factory(get_mqtt_client, self._camera_analyze_object)

    def run(self) -> None:
        camera_width = 640
        camera_height = 480

        self._camera.start()

        # TODO: see issue #78
        self._stream = self.video_stream(self._camera.process_frame, resolution=(
            camera_width, camera_height), framerate=1, pi_camera=False)

    def is_restart_necessary(self, data = None) -> bool:
        new_roi = roi_camera_from_args(data)
        return new_roi != self._camera_analyze_object

    def stop(self, *args) -> None:
        pass

def run_smart_camera_factory():
    return RunSmartCamera(camera_factory, VideoStream)
