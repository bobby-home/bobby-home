import os
from object_detection.detect_people_factory import detect_people_factory
from .camera import Camera
from camera_analyze.camera_analyzer import CameraAnalyzer


def camera_factory(get_mqtt, camera_analyze_object: CameraAnalyzer) -> Camera:
    detect_people = detect_people_factory()

    return Camera(camera_analyze_object, detect_people, get_mqtt, os.environ['DEVICE_ID'])
