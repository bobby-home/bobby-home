from .camera import Camera
import os
from camera.detect_motion import DetectMotion


def camera_factory(get_mqtt_client) -> Camera:
    return Camera(DetectMotion(), get_mqtt_client, os.environ['DEVICE_ID'])
