import os
from object_detection.detect_people_factory import detect_people_factory
from .camera import Camera
from camera_analyze.camera_analyzer import CameraAnalyzer
from .camera_record import CameraRecorder
from .camera_recording import CameraRecording
from mqtt.mqtt_client import get_mqtt


def camera_factory(device_id: str, camera_analyze_object: CameraAnalyzer, camera_recorder: CameraRecorder) -> Camera:
    detect_people = detect_people_factory()

    return Camera(camera_analyze_object, detect_people, get_mqtt, device_id, CameraRecording(device_id, camera_recorder))
