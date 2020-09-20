from .camera import Camera
import os
from camera.detect_motion import DetectPeople


def camera_factory(get_mqtt_client) -> Camera:
    return Camera(DetectPeople(), get_mqtt_client, os.environ['DEVICE_ID'])
