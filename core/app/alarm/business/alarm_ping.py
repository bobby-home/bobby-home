from typing import List
from alarm.models import Ping
from django.db.models import F
from django.utils import timezone


def _update(queryset) -> None:
    queryset.update(
        failures=F('consecutive_failures') + F('failures'),
        consecutive_failures=0,
        last_update=timezone.now()
    )


def reset_ping(device_id: str, service_name: str) -> None:
    _update(Ping.objects.filter(device_id=device_id, service_name=service_name))


def reset_pings(device_ids: List[str], service_name: str) -> None:
    _update(Ping.objects.filter(device_id__in=device_ids, service_name=service_name))


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
        reset_ping(device_id, service_name)
