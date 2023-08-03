from rest_framework import serializers
from .models import EvaluationTask


class EvaluationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationTask
        fields = ('id', 'metricsResult')
