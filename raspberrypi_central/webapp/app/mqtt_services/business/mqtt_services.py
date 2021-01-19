from django.utils import timezone
from mqtt_services.models import MqttServicesConnectionStatusLogs


def is_in_status_since(device_id: str, service_name: str, status: bool, since_time) -> bool:
    """
        Check if the service_name is asked status since the time asked.
        -> If the last registered status is `status` then the function returns True.
    """
    now = timezone.now()

    logs = MqttServicesConnectionStatusLogs.objects.filter(
        device_id=device_id,
        service_name=service_name,
        created_at__range=(since_time, now),).order_by('created_at')

    last_false_result = None
    last_true_result = None

    for log in logs:
        if log.status is not status:
            last_false_result = log.created_at

        if log.status is status:
            last_true_result = log.created_at

    if last_true_result is None:
        return False

    if last_false_result is None:
        return True

    return last_false_result < last_true_result
