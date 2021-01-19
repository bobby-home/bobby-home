from celery import shared_task

from mqtt_services.business.mqtt_services import is_in_status_since
from notification.tasks import send_message
from django.utils.translation import gettext as _


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5},
    default_retry_delay=5
)
def verify_service_status(device_id: str, service_name: str, status: bool, since_time) -> None:
    if not is_in_status_since(device_id, service_name, status, since_time):
        if status:
            send_message(_(f"Your service {service_name} should turn on but the system did not receive any sign of life. Something is wrong."))
        else:
            send_message(_(f'Your service {service_name} should turn off but is still up. Something is wrong.'))


@shared_task()
def mqtt_status_does_not_match_database(device_id: str, received_status: bool, service_name: str):
    if received_status:
        send_message(_(f'Your service {service_name} on device {device_id} has turned on but it should be off. Something is wrong.'))
    else:
        send_message(_(f'Your service {service_name} on device {device_id} has turned off but it should be on. Something is wrong.'))
