from alarm.models import Ping
from devices.models import Device
from django.db.models import Model, F
from django.utils import timezone


def is_status_exists(model_ref: Model, device_id: str, running: bool) -> bool:
    device = Device.objects.get(device_id=device_id)

    status = model_ref.objects.filter(running=running, device=device)
    if status.exists():
        return True

    return False


def register_ping(device_id: str, service_name: str) -> None:
    _obj, created = Ping.objects.get_or_create(
        device_id=device_id, service_name=service_name,
        defaults={
            'last_update': timezone.now(),
            'failures': 0,
            'consecutive_failures': 0
        }
    )
    
    if not created:
        Ping.objects.filter(device_id=device_id, service_name=service_name)\
                .update(failures=F('consecutive_failures') + F('failures'), consecutive_failures=0)

