from rest_framework import serializers
from .models import Heatmap


class HeatmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heatmap
        fields = '__all__'
