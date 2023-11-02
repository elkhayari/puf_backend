from rest_framework import serializers
from .models import Tests, TestOperations, Image, Experiments, UploadMeasurments


# This code specifies the model to work with
# and the fields to be converted to JSON


class TestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tests
        fields = '__all__'


class TestOperationsSerializers(serializers.ModelSerializer):
    class Meta:
        model = TestOperations
        fields = '__all__'


class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['name', 'image']


class ExperimentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Experiments
        fields = '__all__'

# todo delete this


class UploadMeasurmentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = UploadMeasurments
        fields = '__all__'
