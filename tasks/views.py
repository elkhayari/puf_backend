from django.http import JsonResponse
from celery.result import AsyncResult
from .models import EvaluationTask
import base64
import json
from django.http import JsonResponse
from .tasks import calculate_metrics, generate_heatmap_operation
from rest_framework.decorators import api_view
from .serializer import EvaluationResultSerializer
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from .models import Heatmap
from .serializers import HeatmapSerializer


@api_view(["POST"])
def trigger_task(request):
    # Assuming the request payload contains the task name
    data = json.loads(request.body)
    evaluation_title = json.loads(request.body)['title']

    # Create a new Task instance and save it
    taskObject = EvaluationTask.objects.create(title=evaluation_title)

    # Enqueue the long_operation task using Celery
    task = calculate_metrics.delay(taskObject.id, data)
    print(task)

    return JsonResponse({'task_id': taskObject.id})


def task_status(request, task_id):
    task = AsyncResult(task_id)
    print(task.state)
    if task.state == 'PENDING':
        response_data = {'status': 'PENDING', 'progress': 0}
    elif task.state == 'SUCCESS':
        response_data = {'status': 'SUCCESS', 'progress': 100}
    else:
        response_data = {'status': 'RUNNING',
                         'progress': task.info.get('progress', 0)}
    return JsonResponse(response_data)


def tasks(request):
    tasks = EvaluationTask.objects.all().values(
        'id', 'title', 'status', 'start_time', 'finish_time')
    return JsonResponse({'tasks': list(tasks)})


@api_view(["GET"])
def get_result_by_id(request, id):
    print(id)
    try:
        my_evaluation = EvaluationTask.objects.get(id=id)
        # print(my_evaluation.result)
        metrics = my_evaluation.metricsResult
        print(metrics)
        response = {
            'metrics': metrics,
        }
        return JsonResponse(response)
    except EvaluationTask.DoesNotExist:
        return JsonResponse({'error': 'MyModel object not found'}, status=404)


@api_view(["POST"])
def delete_result_by_id(request, id):
    try:
        my_evaluation = EvaluationTask.objects.get(id=id)
        my_evaluation.delete()
        return JsonResponse({'status': 'success'}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'evaluation not found'}, status=404)


@api_view(["POST"])
def generate_heatmaps(request):
    # Assuming the request payload contains the task name
    data_string = json.loads(request.body)
    data = data_string['data']
    evaluation_id = data_string['evaluation_id']
    print(data)
    print(evaluation_id)
    """ evaluation_title = json.loads(request.body)['title']

    # Create a new Task instance and save it
    taskObject = EvaluationTask.objects.create(title=evaluation_title)

    # Enqueue the long_operation task using Celery
    task = calculate_metrics.delay(taskObject.id, data)
    print(task) """

    task = generate_heatmap_operation.delay(data, evaluation_id)

    return JsonResponse({'status': 'started'})


@api_view(["GET"])
def get_existing_heatmap(request):
    evaluation_id = request.GET.get('evaluation_id')
    measurement_ids = json.loads(request.GET.get('measurement_ids'))
    try:
        heatmaps = Heatmap.objects.filter(
            evaluation_result_id=evaluation_id, measurement_ids__in=measurement_ids)
        print(heatmaps)

        data = [{"id": heatmap.id, "heatmap_binary_image": base64.b64encode(heatmap.heatmap_binary_image).decode('utf-8')}
                for heatmap in heatmaps]

        # my_evaluation = EvaluationTask.objects.get(id=id)
        # print(my_evaluation.result)
        # metrics = my_evaluation.metricsResult
        # print(metrics)
        # data = {
        #   'id': 1,
        # }
        return JsonResponse(data, safe=False)
        # return JsonResponse(response)
    except EvaluationTask.DoesNotExist:
        return JsonResponse({'error': 'Heatmap does not exists'}, status=404)
