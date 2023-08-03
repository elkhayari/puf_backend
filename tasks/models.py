from django.db import models
from django.utils import timezone
import json
# Create your models here.


class EvaluationTask(models.Model):
    TASK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ]
    title = models.CharField(max_length=255, null=True)
    task_id = models.CharField(max_length=50, null=True)
    status = models.CharField(
        max_length=20, choices=TASK_STATUS_CHOICES, default='PENDING')
    start_time = models.DateTimeField(auto_now_add=True, null=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    metricsResult = models.JSONField(default=dict)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'COMPLETED' and not self.finish_time:
            self.finish_time = timezone.now()

        super().save(*args, **kwargs)
