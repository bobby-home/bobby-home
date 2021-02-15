from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')

celery = Celery('hello_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery.config_from_object('django.conf:settings', namespace='CELERY')

# setup Periodic Tasks. @see https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html
@celery.on_after_finalize.connect
def setup_periodic_tasks(**kwargs):
    from alarm.tasks import check_pings

    # @todo: does not work.
    # Calls every 60 seconds.
    celery.add_periodic_task(1, check_pings.s())

# Load task modules from all registered Django app configs.
celery.autodiscover_tasks()
