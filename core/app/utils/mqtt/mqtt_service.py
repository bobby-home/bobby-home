from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Type

# fix cyclic import hell.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.mqtt.mqtt_status_handler import OnConnectedHandler

@dataclass
class ServiceDescriptor:
    name: str
    on_connect: Optional[Type[OnConnectedHandler]]

