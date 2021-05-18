from dataclasses import dataclass
from devices.models import Device


@dataclass
class OnMotionData:
    device: Device

