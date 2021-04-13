from dataclasses import dataclass
from typing import Optional
from utils.mqtt.mqtt_status_handler import OnConnectedHandler


@dataclass
class ServiceDescriptor:
    name: str
    on_connect: Optional[OnConnectedHandler]

