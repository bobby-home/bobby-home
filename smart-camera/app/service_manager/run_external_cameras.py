import multiprocessing
import threading
from external_cameras.data import HTTPCameraData
from camera.camera_frame_producer import CameraFrameProducer
from external_cameras.http_camera import HttpCamera
import os
from typing import Dict
import logging
from service_manager.runnable import Runnable


DEVICE_ID = os.environ['DEVICE_ID']
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ConnectedDevices:
    """Wrapper around the datastructures to hold connected devices with their configuration.
    So if we need multiprocessing in the future, we can do it here.
    """

    def __init__(self):
        self._connected_devices: Dict[str, multiprocessing.Process] = {}

    def remove(self, device_id: str) -> None:
        print(self._connected_devices, device_id in self._connected_devices)
        if device_id in self._connected_devices:
            http_camera = self._connected_devices.pop(device_id, None)
            if http_camera:
                LOGGER.info("Stop service and remove ressource for {device_id}.")
                print("Stop service and remove ressource for {device_id}.")
                http_camera.terminate()
            else:
                print("Wanted to stop service for {device_id} but service is not running.")

    def has(self, device_id: str) -> bool:
        return device_id in self._connected_devices

    def add(self, data: HTTPCameraData, device_id: str) -> None:
        LOGGER.info("Start service for {device_id}")
        print("Start service for {device_id}")
        http_camera = HttpCamera(data, device_id)
        process = multiprocessing.Process(target=http_camera.start)
        process.start()
        self._connected_devices[device_id] = process


class RunHTTPExternalCameras(Runnable):
    def __init__(self, connected_devices: ConnectedDevices):
        self._connected_devices = connected_devices

    def run(self, device_id: str, status: bool, data=None) -> None:
        if status is False:
            self._connected_devices.remove(device_id)
            return

        if data is None or 'http' not in data or not isinstance(data['http'], dict):
            return

        if self._connected_devices.has(device_id):
            print(f'Do nothing because service for {device_id} is already running.')
            # do nothing, it's already running.
        else:
            # @todo: error handling here.
            http = HTTPCameraData(**data['http'])
            self._connected_devices.add(http, device_id)

    def __str__(self) -> str:
        return 'run-external-cameras'
