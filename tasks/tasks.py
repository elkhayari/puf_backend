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
import pandas as pd
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
            ids = []
            print('list of measurments')
            for measurment in sublist:
                print(measurment)
                generate_and_save_heatmap(measurment, evaluation_id)
                ids.append(measurment['id'])
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
    # Check if a heatmap with the same measurement_ids already exists
    existing_heatmap = Heatmap.objects.filter(
        measurement_ids=measurment['id']).exists()

    if existing_heatmap:
        print(f"Heatmap for measurement {measurment['id']} already exists.")
    else:
        values = PUFProcessor.read_and_store_input_data(
            file_name, start_addr, stop_addr)

        matrix = PUFProcessor.bytes_to_bit_matrix(values)
        print(type(matrix))
        print(len(matrix))
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
                    "type": "heatmap_update",
                    "message": "Heatmap for measurement generated"
                }
            )
            print('sent')
        except Exception as e:
            print(f"Error saving to database: {e}")


@app.task
def generate_heatmap_robustness_operation(robustness_measurments):
    for item in robustness_measurments:
        for key, value in item.items():
            print(f"Group Key: {key}")
            # Check if a heatmap with the same measurement_ids already exists
            existing_heatmap = Heatmap.objects.filter(
                measurement_ids=key).exists()
            if existing_heatmap:
                print(f"Heatmap for measurement {key} already exists.")
            else:
                matrix_list = []
                initialValue, startAddress, stopAddress = value[
                    'initialValue'], value['startAddress'], value['stopAddress']
                evaluationId = value['evaluationId']
                print(initialValue, startAddress, stopAddress)
                for measurements in value['id_filename_list']:
                    id, filename = measurements['id'], measurements['fileName']
                    print(f"Data for {id} is {filename}:\n")

                    try:
                        meas_values = PUFProcessor.read_and_store_input_data(
                            filename, startAddress, stopAddress)
                        matrix = PUFProcessor.bytes_to_bit_matrix(meas_values)
                        matrix_list.append(matrix)

                    except Exception as e:
                        print(f"Error reading CSV file {filename}:", e)

                robustness_matrix = calculate_robustness(matrix_list)
                print(len(robustness_matrix))
                print(type(robustness_matrix))
                print(robustness_matrix.shape)
                binary_data = PUFPlots.plot_robustness_heatmap(
                    robustness_matrix)

                # resized_matrix = np.resize(robustness_matrix, (200, 200))
                # binary_data = PUFPlots.plot_robustness_heatmap(resized_matrix)
                print(type(binary_data))
                try:
                    Heatmap.objects.create(
                        measurement_ids=key,
                        initial_value=initialValue,
                        heatmap_binary_image=binary_data,
                        evaluation_result_id_id=evaluationId
                    )

                    print('sent')
                except Exception as e:
                    print(f"Error saving to database: {e}")


def calculate_robustness(matrix_list):
    # Stack matrices along a new axis
    stacked_matrices = np.stack(matrix_list, axis=-1)

    # Calculate the mean along the new axis
    robustness_matrix = np.mean(stacked_matrices, axis=-1)

    return robustness_matrix
