from enum import Enum
from utils.mqtt.mqtt_update_status import UpdateStatusDescriptor
from alarm.mqtt.on_status_update import OnUpdateStatus, UpdateStatusPayload


class MqttUpdates(Enum):
    ALARM = 'alarm'


UPDATES = (
    UpdateStatusDescriptor(
        name=MqttUpdates.ALARM.value,
        on_update=OnUpdateStatus,
        payload_type=UpdateStatusPayload
    ),
)
