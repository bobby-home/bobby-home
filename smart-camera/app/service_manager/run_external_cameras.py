from camera.camera_frame_producer import CameraFrameProducer
from external_cameras.http_camera import HttpCamera
import os
from functools import partial
from io import BytesIO
from typing import Dict
from multiprocessing import Process
import logging

from mqtt.mqtt_client import get_mqtt
from camera.camera_config import camera_config
from service_manager.runnable import Runnable
CAMERA_WIDTH = camera_config.camera_width
CAMERA_HEIGHT = camera_config.camera_height

DEVICE_ID = os.environ['DEVICE_ID']
LOGGER = logging.getLogger(__name__)

class ConnectedDevices:
    """
    Wrapper around the datastructures to hold connected devices with their configuration.
    So if we need multiprocessing in the future, we can do it here.
    """

    def __init__(self, mqtt):
        self._mqtt = mqtt
        self._connected_devices: Dict[str, HttpCamera] = {}

    def remove(self, device_id: str) -> None:
        if device_id in self._connected_devices:
            object_detection = self._connected_devices.pop(device_id, None)
            if object_detection:
                pass
                #todo!!!!!
                #object_detection.stop()

    def has(self, device_id: str) -> bool:
        return device_id in self._connected_devices

    def add(self, url: str, device_id: str) -> None:
        camera = CameraFrameProducer(device_id)
        http_camera = HttpCamera(url, camera)
        self._connected_devices[device_id] = http_camera

    @property
    def connected_devices(self) -> Dict[str, HttpCamera]:
        return self._connected_devices


class RunExternalCameras(Runnable):
    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def run(self, device_id: str, status: bool, data=None) -> None:
        if data:
            if 'http_url' in data:
                if status is False:
                   self._connected_devices.remove(device_id)
                else:
                    if self._connected_devices.has(device_id):
                        # do nothing, it's already running.
                        pass
                    else:
                        self._connected_devices.add(data['http_url'], device_id)

    def __str__(self) -> str:
        return 'run-external-cameras'
