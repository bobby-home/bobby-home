from .camera import Camera
import os
from object_detection.detect_people import DetectPeople
from camera_analyze.camera_analyzer import CameraAnalyzer


def camera_factory(get_mqtt_client, camera_analyze_object: CameraAnalyzer) -> Camera:
    return Camera(camera_analyze_object, DetectPeople(), get_mqtt_client, os.environ['DEVICE_ID'])
