from django.utils import timezone
from mqtt_services.models import MqttServicesConnectionStatusLogs


def is_in_status_since(device_id: str, service_name: str, status: bool, since_time) -> bool:
    """
    Check if the (device_id,service_name) status is equals to the `status` since the time asked.
    -> If the last registered status is `status` then the function returns True, otherwise False.
    It is used to check if a (device_id,service_name) actually turned `status`
    when the system asked for it.
    """
    now = timezone.now()

    """
    We could have used two queries:
    - ok_logs with status=status
    - ko_logs with status=not status
    and check if ok_logs and ko_logs.created_at < ok_logs.created_at to return True.
    But this method still needs some python logic and two heavy queries.
    So, we decided to do it with one query and a bit of python logic.
    """
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
