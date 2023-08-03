from rest_framework import serializers
from .models import SharedTestsModel, ReliabilityTestsModel, WriteLatencyTestsModel, ReadLatencyTestsModel, RowHammeringTestsModel, ReliabilityMeasurmentTestsModel, SharedMeasurmentTestsModel, ReadLatencyMeasurmentTestsModel, WriteLatencyMeasurmentTestsModel, RowHammeringMeasurmentTestsModel


class SharedTestsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedTestsModel
        fields = '__all__'


class ReliabilityTestsModelSerializer(SharedTestsModelSerializer):
    class Meta:
        model = ReliabilityTestsModel
        fields = '__all__'


class WriteLatencyTestsModelSerializer(SharedTestsModelSerializer):
    class Meta:
        model = WriteLatencyTestsModel
        fields = '__all__'


class ReadLatencyTestsModelSerializer(SharedTestsModelSerializer):
    class Meta:
        model = ReadLatencyTestsModel
        fields = '__all__'


class RowHammeringTestsModelSerializer(SharedTestsModelSerializer):
    class Meta:
        model = RowHammeringTestsModel
        fields = '__all__'

########################
# Measurments operations
########################


class SharedMeasurmentTestsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedMeasurmentTestsModel
        fields = '__all__'


class ReliabilityMeasurmentTestsModelSerializer(SharedMeasurmentTestsModelSerializer):
    class Meta:
        model = ReliabilityMeasurmentTestsModel
        fields = '__all__'


class WriteLatencyMeasurmentTestsModelSerializer(SharedMeasurmentTestsModelSerializer):
    class Meta:
        model = WriteLatencyMeasurmentTestsModel
        fields = '__all__'


class ReadLatencyMeasurmentTestsModelSerializer(SharedMeasurmentTestsModelSerializer):
    class Meta:
        model = ReadLatencyMeasurmentTestsModel
        fields = '__all__'


class RowHammeringMeasurmentTestsModelSerializer(SharedMeasurmentTestsModelSerializer):
    class Meta:
        model = RowHammeringMeasurmentTestsModel
        fields = '__all__'
