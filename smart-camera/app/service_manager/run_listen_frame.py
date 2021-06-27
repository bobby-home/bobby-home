from typing import Dict

from camera.camera_recording import CameraRecording, NoCameraRecording
from camera.camera_object_detection import CameraObjectDetection
from camera.camera_object_detection_factory import camera_object_detection_factory
from camera.camera_record import CameraRecorder, DumbCameraRecorder
from object_detection.detect_people_factory import detect_people_factory
from service_manager.runnable import Runnable

DETECT_PEOPLE = detect_people_factory()

def camera_factory(mqtt, device_id: str, video_support: bool) -> CameraObjectDetection:
    if video_support is False:
        camera_recording = NoCameraRecording()
    else:
        camera_recorder = DumbCameraRecorder(mqtt.client, device_id)
        camera_recording = CameraRecording(mqtt.client, device_id, camera_recorder)

    camera = camera_object_detection_factory(device_id, camera_recording, DETECT_PEOPLE)
    camera.start()

    return camera

class ConnectedDevices:
    """
    Wrapper around the datastructures to hold connected devices with their configuration.
    So if we need multiprocessing in the future, we can do it here.
    """

    def __init__(self, mqtt):
        self._mqtt = mqtt
        self._connected_devices: Dict[str, CameraObjectDetection] = {}

    def remove(self, device_id: str) -> None:
        if device_id in self._connected_devices:
            object_detection = self._connected_devices.pop(device_id, None)
            if object_detection:
                object_detection.stop()

    def has(self, device_id: str) -> bool:
        return device_id in self._connected_devices

    def add(self, device_id: str, video_support: bool) -> None:
        camera = camera_factory(self._mqtt, device_id, video_support)
        self._connected_devices[device_id] = camera

    @property
    def connected_devices(self) -> Dict[str, CameraObjectDetection]:
        return self._connected_devices


class RunListenFrame(Runnable):

    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def run(self, device_id: str, status: bool, data=None) -> None:
        print(f'run listen frame, data={data}')

        if status is False:
            self._connected_devices.remove(device_id)
            return None

        if self._connected_devices.has(device_id):
            return
        
        to_analyze = data.get('to_analyze', False)
        if to_analyze is True:
            video_support = data.get('video_support', True)
            self._connected_devices.add(device_id, video_support)
