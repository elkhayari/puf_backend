# urls.py
from django.urls import path
from tasks.views import trigger_task, task_status, tasks, get_result_by_id, delete_result_by_id

urlpatterns = [
    path('trigger-evaluation/', trigger_task, name='trigger_task'),
    path('task-status/<str:task_id>/', task_status, name='task_status'),
    path('tasks/', tasks, name='tasks'),
    path('evaluation-result/<int:id>/',
         get_result_by_id, name='get_result_by_id'),
    path('delete-result/<int:id>/', delete_result_by_id,
         name='delete_result_by_id'),



]
