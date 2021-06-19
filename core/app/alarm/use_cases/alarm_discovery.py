import json
from utils.mqtt import mqtt_factory
import uuid
from alarm.models import AlarmStatus
from devices.models import Device, DeviceType
from alarm.use_cases.data import DiscoverAlarmData


def discover_alarm(in_data: DiscoverAlarmData) -> None:
    device_id = uuid.uuid4().__str__().split('-')[0]
    i_device_type, _created_type = DeviceType.objects.get_or_create(
        type=in_data.type,
        defaults={'type': in_data.type},
    )

    # todo: while exists, renegerate uuid. Edge case! but could happen.
    device = Device.objects.create(
        name=f'discovered_{device_id}',
        device_id=device_id,
        device_type=i_device_type,
    )

    AlarmStatus.objects.create(
        running=False,
        device=device,
    )

    payload = {
        'device_id': device_id,
        'id': in_data.id,
    }

    mqtt_factory().publish('registered/alarm', json.dumps(payload))

