from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import time
from datetime import datetime
from .models import EvaluationTask
from celery import shared_task
from puf_server.views import getMetrics
import json
import numpy as np
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pufBackend.settings')

app = Celery('pufBackend')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        return super().default(obj)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task
def execute_task(seconds):
    print('**** hi from execute_task')
    time.sleep(seconds)
    return f"Task completed in {seconds} seconds"


@app.task
def long_operation(task_id, data):
    # Retrieve the task using the provided task_id
    print('Start Long Operation')

    try:
        task = EvaluationTask.objects.get(id=task_id)
        print(task.id)

        # Update the task status as needed
        task.status = 'IN_PROGRESS'
        task.save()

        time.sleep(5)  # Replace with your actual long operation
        evaluationResult = getMetrics(data)
        # print(evaluationResult)

        # Update the task status upon completion
        task.metricsResult = json.dumps(evaluationResult, cls=NumpyJSONEncoder)

        task.status = 'COMPLETED'
        task.finish_time = datetime.now()
        print('SAVE')
        print(task.status)
        print(task.metricsResult)
        task.save()

    except Exception as e:
        # Handle any exceptions and update task status accordingly
        task = EvaluationTask.objects.get(id=task_id)
        task.finish_time = datetime.now()
        task.status = 'FAILED'
        task.save()

        # Re-raise the exception to be logged in the Celery worker's error log
        raise e


@shared_task
def save_data_to_model(model_id, data):
    try:
        # Get the model instance by ID
        model_instance = EvaluationTask.objects.get(id=model_id)

        # Update the JSONField with the new data
        model_instance.result = data
        model_instance.save()

        return True
    except EvaluationTask.DoesNotExist:
        # Handle the case when the model instance does not exist
        return False


@shared_task
def send_device_notification():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'devices', {'type': 'notify.devices'})
