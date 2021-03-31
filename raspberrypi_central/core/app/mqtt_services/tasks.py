from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from devices.models import Device
from mqtt_services.business.mqtt_services import is_in_status_since, is_last_status
from mqtt_services.models import MqttServicesConnectionStatusLogs
import mqtt_services.notifications as notifications


@shared_task()
def verify_service_status(device_id: str, service_name: str, status: bool, since_time) -> None:
    """
    Task to verify if a service has turned `status` since a given time.
    Usage: when the system sends a mqtt message to change the status of a service and it want to check if the status of the service actually changed.
    Generally, it is used with a countdown of some seconds to let the service the time to change.
    """
    if not is_in_status_since(device_id, service_name, status, since_time) and not is_last_status(device_id, service_name, status):
        device = Device.objects.with_location().get(device_id=device_id)
        notifications.service_status(service_name, status, device)


@shared_task()
def mqtt_status_does_not_match_database(device_id: str, received_status: bool, service_name: str):
    """
    Task to react when the system received a mqtt status that does not match to the database status.
    For example, in the database the alarm status is on and the system receives a mqtt message that indicates a disconnect
    from the alarm.
    That indicates a failure in the system.
    """
    device = Device.objects.with_location().get(device_id=device_id)
    notifications.mqtt_status_does_not_match_database(service_name, received_status, device)


@shared_task()
def cleanup() -> None:
    how_many_hour = 1
    MqttServicesConnectionStatusLogs.objects.filter(created_at__lte=timezone.now() - timedelta(hours=how_many_hour)).delete()
