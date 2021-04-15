from alarm.mqtt.on_connected_services import OnConnectedDumbCamera, OnConnectedObjectDetectionHandler, OnConnectedSpeakerHandler
from utils.mqtt.mqtt_service import ServiceDescriptor
from alarm.mqtt.mqtt import register


SERVICES = (
    ServiceDescriptor(
        name='object_detection',
        on_connect=OnConnectedObjectDetectionHandler
    ),
    ServiceDescriptor(
        name='camera',
        on_connect=OnConnectedDumbCamera
    ),
    ServiceDescriptor(
        name='speaker',
        on_connect=OnConnectedSpeakerHandler
    ),
)

