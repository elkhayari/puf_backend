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
from puf_server.utils.PUFProcessor import PUFProcessor
from puf_server.utils.PUFPlots import PUFPlots
from .models import Heatmap
from .serializers import HeatmapSerializer
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
def calculate_metrics(task_id, data):
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


@app.task
def generate_heatmap_operation(data, evaluation_id):
    channel_layer = get_channel_layer()
    print('Start generating the heatmaps')
    print(data)
    for sublist in data:
        print('sublist -----')
        if len(sublist) == 1:
            generate_and_save_heatmap(sublist[0], evaluation_id)

        else:
            summed_data = None
            ids = []
            print('list of measurments')
            for measurment in sublist:

                print(measurment)
                generate_and_save_heatmap(measurment, evaluation_id)
                """ if summed_data is None:
                    summed_data = df
                else:
                    summed_data += df
                binary_data = generate_heatmap(df, entry['id'])
                heatmap = Heatmap(id=entry['id'], initialvalue=entry['initialValue'], heatmap_image=binary_data)
                heatmap.save()"""
                ids.append(measurment['id'])
            """binary_data = generate_heatmap(summed_data, "Summed Heatmap for Sublist")
            heatmap = Heatmap(id=",".join(ids), initialvalue=sublist[0]['initialValue'], heatmap_image=binary_data)
            heatmap.save() """
            print(ids)
        print('----------')
    time.sleep(5)
    async_to_sync(channel_layer.group_send)(
        "heatmap_group",
        {
            "type": "heatmap.update",
            "message": "Heatmap generation complete"
        }
    )


def generate_and_save_heatmap(measurment, evaluation_id):
    channel_layer = get_channel_layer()
    file_name, start_addr, stop_addr = measurment[
        'fileName'], measurment['startAddress'], measurment['stopAddress']
    print(file_name, start_addr, stop_addr)
    values = PUFProcessor.read_and_store_input_data(
        file_name, start_addr, stop_addr)

    matrix = PUFProcessor.bytes_to_bit_matrix(values)
    binary_data = PUFPlots.create_heatmap_array(matrix)

    try:
        heatmap = Heatmap.objects.create(
            measurement_ids=measurment['id'],
            initial_value=measurment['initialValue'],
            heatmap_binary_image=binary_data,
            evaluation_result_id_id=evaluation_id
        )
        async_to_sync(channel_layer.group_send)(
                "heatmap_group",
                {
                    "type": "heatmap.update",
                    "message": f"Heatmap for measurement {measurment['id']} generated"
                }
            )
    except Exception as e:
        print(f"Error saving to database: {e}")
