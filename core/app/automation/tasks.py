from typing import Dict, Optional
from automation.models import Automation
from celery import shared_task

from automation.actions.action_mqtt_publish import mqtt_publish
from automation.actions import Triggers


def _run_automations(trigger_name: Triggers) -> None:
    automations = Automation.objects.filter(trigger_name=trigger_name.value)

    for automation in automations:
        actions = automation.actions_mqtt_publish.all()
        mqtt_publish(actions)


@shared_task()
def on_motion_detected(*_args, **_kwargs) -> None:
    _run_automations(Triggers.ON_MOTION_DETECTED)

@shared_task()
def on_motion_left(*_args, **_kwargs) -> None:
    _run_automations(Triggers.ON_MOTION_LEFT)

