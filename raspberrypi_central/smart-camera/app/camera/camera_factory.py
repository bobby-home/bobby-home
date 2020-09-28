from .camera import Camera
import os
from camera.detect_motion import DetectPeople
from camera.camera_roi import ROICamera


def camera_factory(get_mqtt_client, camera_roi: ROICamera) -> Camera:
    return Camera(camera_roi, DetectPeople(), get_mqtt_client, os.environ['DEVICE_ID'])
