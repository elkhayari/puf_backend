from rest_framework import serializers
from .models import TtyDeviceModel

# This code specifies the model to work with


class TtyDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TtyDeviceModel
        fields = '__all__'
