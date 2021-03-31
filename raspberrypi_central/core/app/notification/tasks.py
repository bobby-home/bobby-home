from celery import shared_task

from devices.models import Device
from .models import SystemNotification
from .consts import SeverityChoice
from notification.out.messaging import messaging_factory


@shared_task
def send_picture(picture_path: str):
    print(f'task send_picture: picture_path={picture_path}')
    messaging = messaging_factory()
    messaging.send_picture(picture_path)

@shared_task
def send_video(video_path: str):
    print(f'task send_video: video_path={video_path}')
    messaging = messaging_factory()
    messaging.send_video(video_path)

@shared_task
def send_message(message: str):
    messaging = messaging_factory()
    messaging.send_message(message)


@shared_task
def send_alert_notification(pk: int) -> None:
    alert = SystemNotification.objects.get(pk=pk)
    messaging = messaging_factory()
    messaging.send_message(message=alert.message)


@shared_task
def create_and_send_notification(severity: SeverityChoice, device_id: str, message: str) -> None:
    alert = SystemNotification.objects.create(message=message, severity=severity)

    device = Device.objects.get(device_id=device_id)
    alert.devices.add(device.pk)

    send_alert_notification.apply_async(kwargs={'pk': alert.pk})
