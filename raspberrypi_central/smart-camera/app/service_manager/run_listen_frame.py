from typing import Dict

from camera.camera import Camera
from camera.camera_factory import camera_factory
from camera.camera_record import DumbCameraRecorder
from camera_analyze.camera_analyzer import CameraAnalyzer
from object_detection.detect_people_factory import detect_people_factory
from service_manager.roi_camera_from_args import roi_camera_from_args
from service_manager.runnable import Runnable

DETECT_PEOPLE = detect_people_factory()

def dumb_camera_factory(mqtt, device_id: str, camera_analyzer: CameraAnalyzer) -> Camera:
    camera_record = DumbCameraRecorder(mqtt.client, device_id)
    camera = camera_factory(device_id, camera_analyzer, camera_record, DETECT_PEOPLE)
    camera.start()

    return camera

class ConnectedDevices:
    """
    Wrapper around the datastructures to hold connected devices with their configuration.
    So if we need multiprocessing in the future, we can do it here.
    """

    def __init__(self, mqtt):
        self._mqtt = mqtt
        self._connected_devices: Dict[str, Camera] = {}

    def remove(self, device_id: str) -> None:
        if device_id in self._connected_devices:
            self._connected_devices.pop(device_id, None)

    def has(self, device_id: str) -> bool:
        return device_id in self._connected_devices

    def update(self, device_id: str, camera_analyzer: CameraAnalyzer) -> None:
        if not self.has(device_id):
            return None

        camera = self._connected_devices[device_id]

        if camera.analyze_motion != camera_analyzer:
            self._connected_devices[device_id].analyze_motion = camera_analyzer

    def add(self, device_id: str, camera_analyzer: CameraAnalyzer) -> None:
        camera = dumb_camera_factory(self._mqtt, device_id, camera_analyzer)
        self._connected_devices[device_id] = camera

    @property
    def connected_devices(self) -> Dict[str, Camera]:
        return self._connected_devices


class RunListenFrame(Runnable):

    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def run(self, device_id: str, status: bool, data=None) -> None:
        if data is not None:
            is_dumb = data.get('is_dumb', False)
            if is_dumb is False:
                return None

        if status is False:
            self._connected_devices.remove(device_id)
            return None

        camera_analyze_object = roi_camera_from_args(data)

        if self._connected_devices.has(device_id):
            pass
            # todo: check if analyzer differ to remove/add new config
            # try to keep the same Camera object to avoid mqtt disconnect/reconnect.
            # could be able to do it because its a composition
        else:
            self._connected_devices.add(device_id, camera_analyze_object)
