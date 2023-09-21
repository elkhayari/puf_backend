# urls.py
from django.urls import path
from tasks.views import trigger_task, task_status, tasks, get_result_by_id, delete_result_by_id, generate_heatmaps, get_existing_heatmap, check_heatmap_ids, generate_rebustness_heatmap, get_robustness_heatmap

urlpatterns = [
    path('trigger-evaluation/', trigger_task, name='trigger_task'),
    path('task-status/<str:task_id>/', task_status, name='task_status'),
    path('tasks/', tasks, name='tasks'),
    path('evaluation-result/<int:id>/',
         get_result_by_id, name='get_result_by_id'),
    path('delete-result/<int:id>/', delete_result_by_id,
         name='delete_result_by_id'),
    path('generate-heatmaps/', generate_heatmaps,
         name='generate_heatmaps'),
    path('existing-heatmap-ids/', get_existing_heatmap,
         name='get_existing_heatmap'),
    path('check-heatmap-ids/', check_heatmap_ids, name='check_heatmap_ids'),
    path('generate-rebustness-heatmaps/', generate_rebustness_heatmap,
         name='generate_rebustness_heatmap'),
    path('robustness-heatmap/', get_robustness_heatmap,
         name='get_robustness_heatmap')





]
