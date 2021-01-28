from devices.models import Device
from django.db.models import Model


def is_status_exists(model_ref: Model, device_id: str, running: bool) -> bool:
    device = Device.objects.get(device_id=device_id)

    status = model_ref.objects.filter(running=running, device=device)
    if status.exists():
        return True

    return False
