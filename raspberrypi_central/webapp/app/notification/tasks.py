from celery import shared_task
from .messaging import Messaging


@shared_task
def send_message(*args, **kwargs):
    messaging = Messaging()
    messaging.send_message(*args, **kwargs)
