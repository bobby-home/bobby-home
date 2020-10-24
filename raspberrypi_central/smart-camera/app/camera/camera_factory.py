from .camera import Camera
import os
from camera.detect_motion import DetectPeople
from .camera_analyze import CameraAnalyzeObject


def camera_factory(get_mqtt_client, camera_analyze_object: CameraAnalyzeObject) -> Camera:
    return Camera(camera_analyze_object, DetectPeople(), get_mqtt_client, os.environ['DEVICE_ID'])
