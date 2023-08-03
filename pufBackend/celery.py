from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import time


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pufBackend.settings')

app = Celery('pufBackend')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

print('#### hhhh')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
