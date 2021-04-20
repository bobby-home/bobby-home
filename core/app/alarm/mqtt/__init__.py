from enum import Enum
from alarm.mqtt.on_connected_services import OnConnectedDumbCamera, OnConnectedObjectDetectionHandler, OnConnectedSpeakerHandler
from utils.mqtt.mqtt_service import ServiceDescriptor
from camera.mqtt import MqttServices as CameraMqttServices

class MqttServices(Enum):
    OBJECT_DETECTION_MANAGER = 'object_detection_manager'
    OBJECT_DETECTION = 'object_detection'

    SPEAKER = 'speaker'


SERVICES = (
    ServiceDescriptor(
        name=MqttServices.OBJECT_DETECTION.value,
        on_connect=OnConnectedObjectDetectionHandler
    ),
    ServiceDescriptor(
        name=CameraMqttServices.CAMERA.value,
        on_connect=OnConnectedDumbCamera
    ),
    ServiceDescriptor(
        name=MqttServices.SPEAKER.value,
        on_connect=OnConnectedSpeakerHandler
    ),
)

