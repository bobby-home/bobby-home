from alarm.models import Ping
from devices.models import Device
from django.db.models import Model
from django.utils import timezone


def is_status_exists(model_ref: Model, device_id: str, running: bool) -> bool:
    device = Device.objects.get(device_id=device_id)

    status = model_ref.objects.filter(running=running, device=device)
    if status.exists():
        return True

    return False

def register_ping(device_id: str, service_name: str) -> None:
    Ping.objects.update_or_create(
        device_id=device_id, service_name=service_name,
        defaults={'last_update': timezone.now()}
    )
