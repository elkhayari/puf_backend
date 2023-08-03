from rest_framework import serializers
from .models import ScharedUploadMeasurmentsModel, UploadReliabilityMeasurmentModel, UploadWriteLatencyMeasurmentModel, UploadReadLatencyMeasurmentModel, UploadRowHammeringMeasurmentModel

# Serializer for SharedModel


class ScharedUploadMeasurmentsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScharedUploadMeasurmentsModel
        fields = '__all__'

# Serializer for reliabilitySchema


class UploadReliabilityMeasurmentModelSerializer(ScharedUploadMeasurmentsModelSerializer):
    class Meta:
        model = UploadReliabilityMeasurmentModel
        fields = '__all__'

# Serializer for writeLatencySchema


class UploadWriteLatencyMeasurmentModelSerializer(ScharedUploadMeasurmentsModelSerializer):
    class Meta:
        model = UploadWriteLatencyMeasurmentModel
        fields = '__all__'

# Serializer for readLatencySchema


class UploadReadLatencyMeasurmentModelSerializer(ScharedUploadMeasurmentsModelSerializer):
    class Meta:
        model = UploadReadLatencyMeasurmentModel
        fields = '__all__'

# Serializer for rowHammeringSchema


class UploadRowHammeringMeasurmentModelSerializer(ScharedUploadMeasurmentsModelSerializer):
    class Meta:
        model = UploadRowHammeringMeasurmentModel
        fields = '__all__'
