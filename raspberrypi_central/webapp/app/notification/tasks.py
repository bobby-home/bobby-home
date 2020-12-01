from celery import shared_task

from devices.models import Device
from .models import SeverityChoice, SystemNotification
from notification.out.messaging import Messaging


@shared_task
def send_message(*args, **kwargs):
    messaging = Messaging()
    messaging.send_message(*args, **kwargs)


@shared_task()
def send_alert_notification(pk: int) -> None:
    alert = SystemNotification.objects.get(pk=pk)
    messaging = Messaging()
    messaging.send_message(message=alert.message)


@shared_task
def create_and_send_notification(device_id: str, message: str):
    alert = SystemNotification.objects.create(message=message, severity=SeverityChoice.HIGH)

    device = Device.objects.get(device_id=device_id)
    alert.devices.add(device.pk)

    send_alert_notification.apply_async(kwargs={'pk': alert.pk})
