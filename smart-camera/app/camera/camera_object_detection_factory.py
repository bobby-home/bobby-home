import os
from camera.camera_object_detection_data import CameraObjectDetectionData
from typing import Optional

from object_detection.detect_people import DetectPeople
from object_detection.detect_people_factory import detect_people_factory
from .camera_object_detection import CameraObjectDetection
from .camera_record import CameraRecorder
from .camera_recording import CameraRecording
from mqtt.mqtt_client import get_mqtt


def camera_object_detection_factory(device_id: str, camera_recorder: CameraRecorder, detect_people: Optional[DetectPeople] = None) -> CameraObjectDetection:
    if detect_people is None:
        detect_people = detect_people_factory()

    data = CameraObjectDetectionData(
        seconds_lapsed_to_trigger_motion=int(os.getenv('KEY', 3)),
        seconds_lapsed_to_trigger_no_motion=int(os.getenv('', 60)),
    )

    return CameraObjectDetection(detect_people, get_mqtt, data, device_id, CameraRecording(device_id, camera_recorder))
