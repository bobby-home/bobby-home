from __future__ import absolute_import, unicode_literals

import os
from uuid import uuid4

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')

celery = Celery('hello_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery.config_from_object('django.conf:settings', namespace='CELERY')

# https://docs.celeryproject.org/en/stable/getting-started/brokers/redis.html#id1
# The value must be an int describing the number of seconds.
celery.conf.broker_transport_options = {'visibility_timeout': 600}

# setup Periodic Tasks. @see https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html
@celery.on_after_finalize.connect
def setup_periodic_tasks(**_kwargs):
    # Calls every 65 seconds.
    celery.add_periodic_task(65, periodic_check_pings.s())

    # every minutes check if we need to split some video recording
    # (because of a motion detection)
    celery.add_periodic_task(60, periodic_split_recordings.s())

    # Executes every Sunday morning at 9:30 a.m.
    celery.add_periodic_task(
        crontab(hour=9, minute=30, day_of_week=0),
        backend_cleanup.s(),
    )

# Load task modules from all registered Django app configs.
celery.autodiscover_tasks()

@celery.task
def periodic_check_pings() -> None:
    """
    Weird "hack" to make the periodic_task works.
    I lost soo many hours to make this works,
    huge thanks to: https://stackoverflow.com/a/46965132

    Returns
    -------
    None
    """
    from alarm.tasks import check_pings
    check_pings()

@celery.task
def backend_cleanup() -> None:
    from mqtt_services.tasks import cleanup
    cleanup()

@celery.task
def periodic_split_recordings() -> None:
    from alarm.use_cases.alarm_camera_video_manager import alarm_camera_video_manager_factory
    manager = alarm_camera_video_manager_factory()
    manager.split_recordings(str(uuid4()))
