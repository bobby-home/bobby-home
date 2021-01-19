from django.utils import timezone

from mqtt_services.models import MqttServicesConnectionStatusLogs


def is_in_status_since(device_id: str, service_name: str, status: bool, since_time) -> bool:
    now = timezone.now()

    ok_logs = MqttServicesConnectionStatusLogs.objects.filter(
        device_id=device_id,
        service_name=service_name,
        status=status,
        created_at__range=(since_time, now),)

    ko_logs = MqttServicesConnectionStatusLogs.objects.filter(
        device_id=device_id,
        service_name=service_name,
        status=not status,
        created_at__range=(since_time, now),)

    if ko_logs.exists():
        return False

    if ok_logs.exists():
        return True

    return False
