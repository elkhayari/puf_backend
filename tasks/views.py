from django.http import JsonResponse
from celery.result import AsyncResult
from .models import EvaluationTask
import json
from django.http import JsonResponse
from .tasks import long_operation
from rest_framework.decorators import api_view
from .serializer import EvaluationResultSerializer
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist


@api_view(["POST"])
def trigger_task(request):
    # Assuming the request payload contains the task name
    data = json.loads(request.body)
    evaluation_title = json.loads(request.body)['title']

    # Create a new Task instance and save it
    taskObject = EvaluationTask.objects.create(title=evaluation_title)

    # Enqueue the long_operation task using Celery
    task = long_operation.delay(taskObject.id, data)
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
