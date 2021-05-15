from typing import Any, Dict, Optional
from automation.models import Automation
from celery import shared_task

from automation.actions.action_mqtt_publish import mqtt_publish
from automation.actions import Triggers
from automation.dataclasses import OnMotionData
from devices.models import Device


actions = [
    {
        'related_name': 'actions_mqtt_publish',
        'action': mqtt_publish
    }
]


def _run_automations(trigger_name: Triggers, data: Optional[Any] = None) -> None:
    automations = Automation.objects.filter(trigger_name__contains=[trigger_name.name])
    
    for automation in automations:
        actions = automation.actions_mqtt_publish.all()
        mqtt_publish(actions, data)

def _motion_data(data):
    d = None

    if data and 'device_id' in data:
        device = Device.objects.get(device_id=data['device_id'])
        d = OnMotionData(device=device)
    
    return d


@shared_task()
def on_motion_detected(*_args, data: Dict[str, str]) -> None:
    d = _motion_data(data)
    _run_automations(Triggers.ON_MOTION_DETECTED, d)


@shared_task()
def on_motion_left(*_args, data: Dict[str, str]) -> None:
    d = _motion_data(data)
    _run_automations(Triggers.ON_MOTION_LEFT)

