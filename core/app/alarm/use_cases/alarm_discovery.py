import json
from utils.mqtt import mqtt_factory
import uuid
from alarm.models import AlarmStatus
from devices.models import Device, DeviceType
from alarm.use_cases.data import DiscoverAlarmData

def _get_device(in_data: DiscoverAlarmData) -> Device:
    if in_data.device_id:
        device_id = in_data.device_id
        device = Device.objects.get(device_id=device_id)
        return device

    if in_data.mac_address:
        try:
            device = Device.objects.get(mac_address=in_data.mac_address)
            return device
        except Device.DoesNotExist:
            # it is ok, we will create it.
            pass

    # unkown device_id, need to create it.
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

    return device


def discover_alarm(in_data: DiscoverAlarmData) -> None:
    device = _get_device(in_data) 

    AlarmStatus.objects.get_or_create(
        device=device,
        defaults={'device': device},
    )

    payload = {
        'device_id': device.device_id,
        'id': in_data.id,
    }

    mqtt_factory().publish('registered/alarm', json.dumps(payload))

