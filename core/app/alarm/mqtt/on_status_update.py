from typing import Optional
from devices.models import Device
from alarm.models import AlarmStatus
from alarm.use_cases.alarm_status import AlarmChangeStatus
from dataclasses import dataclass, field
from distutils.util import strtobool
from utils.mqtt.mqtt_update_status import OnUpdateStatusHandler


@dataclass
class UpdateStatusPayload:
    status: str
    force: str = 'off'

    status_bool: Optional[bool] = field(init=False, default=None)
    force_bool: Optional[bool] = field(init=False, default=None)
    toggle: Optional[bool] = field(init=False, default=None)

    def __post_init__(self):
        if self.status == 'toggle':
            self.toggle = True
        else:
            self.status_bool = strtobool(self.status) == 1
            self.force_bool = strtobool(self.force) == 1 


class OnUpdateStatus(OnUpdateStatusHandler):

    def on_toggle_device(self, data_payload, device_id: str) -> None:
        device = Device.objects.get(device_id=device_id)
        AlarmChangeStatus.reverse_status(device.alarmstatus.pk, force=data_payload.force_bool)

    def on_update_device(self, data_payload, device_id: str) -> None:
        alarm_status = AlarmStatus.objects.get(device__device_id=device_id)
        alarm_status.running = data_payload.status_bool
        AlarmChangeStatus.save_status(alarm_status, force=data_payload.force_bool)

    def on_update_all(self, data_payload: UpdateStatusPayload) -> None:
        AlarmChangeStatus.all_change_status(status=data_payload.status_bool, force=data_payload.force_bool)

