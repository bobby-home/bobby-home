
from alarm.models import AlarmStatus
from alarm.use_cases.alarm_status import AlarmChangeStatus
from dataclasses import dataclass, field
from distutils.util import strtobool
from utils.mqtt.mqtt_update_status import OnUpdateStatusHandler


@dataclass
class UpdateStatusPayload:
    status: str
    force: str

    status_bool: bool = field(init=False)
    force_bool: bool = field(init=False)

    def __post_init__(self):
        self.status_bool = strtobool(self.status) == 1
        self.force_bool = strtobool(self.force) == 1 


class OnUpdateStatus(OnUpdateStatusHandler):

    @abstractmethod
    def on_update_device(self, data_payload, device_id: str) -> None:
        alarm_status = AlarmStatus.objects.get(device__device_id=device_id)
        alarm_status.running = data_payload.status_bool
        AlarmChangeStatus.save_status(alarm_status)

    @abstractmethod
    def on_update_all(self, data_payload: UpdateStatusPayload) -> None:
        AlarmChangeStatus.all_change_status(status=data_payload.status_bool, force=data_payload.force_bool)

