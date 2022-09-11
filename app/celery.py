from __future__ import absolute_import

import os

from celery import Celery
from django.apps import apps
from kombu.entity import Exchange, Queue

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")
app = Celery("app")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
app.conf.task_default_queue = "default"
app.conf.task_queues = (
    Queue(
        "default",
        Exchange("normal"),
        routing_key="default",
        queue_arguments={"x-max-priority": 10},
    ),
)
CELERY_DEFAULT_QUEUE = "normal"
CELERY_DEFAULT_EXCHANGE = "normal"
CELERY_DEFAULT_ROUTING_KEY = "default"
