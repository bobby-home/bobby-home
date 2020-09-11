from .camera import Camera
import os


def camera_factory(get_mqtt_client) -> Camera:
    return Camera(get_mqtt_client, os.environ['DEVICE_ID'])
