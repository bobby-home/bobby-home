from enum import Enum
from utils.mqtt.mqtt_update_status import UpdateStatusDescriptor
from alarm.mqtt.on_connected_services import OnConnectedCamera, OnConnectedCameraManager, OnConnectedObjectDetection, OnConnectedSpeakerHandler
from alarm.mqtt.on_status_update import OnUpdateStatus, UpdateStatusPayload
from utils.mqtt.mqtt_service import ServiceDescriptor
from camera.mqtt import MqttServices as CameraMqttServices


class MqttServices(Enum):
    OBJECT_DETECTION_MANAGER = 'object_detection_manager'
    OBJECT_DETECTION = 'object_detection'

    SPEAKER = 'speaker'


class MqttUpdates(Enum):
    ALARM = 'alarm'


SERVICES = (
    ServiceDescriptor(
        name=MqttServices.OBJECT_DETECTION.value,
        on_connect=OnConnectedObjectDetection
    ),
    ServiceDescriptor(
        name=CameraMqttServices.CAMERA_MANAGER.value,
        on_connect=OnConnectedCameraManager
    ),
     ServiceDescriptor(
        name=CameraMqttServices.CAMERA.value,
        on_connect=OnConnectedCamera
    ),
    ServiceDescriptor(
        name=MqttServices.SPEAKER.value,
        on_connect=OnConnectedSpeakerHandler
    ),
)

UPDATES = (
    UpdateStatusDescriptor(
        name=MqttUpdates.ALARM.value,
        on_update=OnUpdateStatus,
        payload_type=UpdateStatusPayload
    ),
)
