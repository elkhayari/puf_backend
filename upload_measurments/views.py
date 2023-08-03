from django.shortcuts import render
import re
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .models import UploadReliabilityMeasurmentModel, UploadWriteLatencyMeasurmentModel, UploadReadLatencyMeasurmentModel, UploadRowHammeringMeasurmentModel
from .serializers import UploadReliabilityMeasurmentModelSerializer, UploadWriteLatencyMeasurmentModelSerializer, UploadReadLatencyMeasurmentModelSerializer, UploadRowHammeringMeasurmentModelSerializer

regex_pattern = re.compile(
    r'(read|write|row hammering|reliability).*', re.IGNORECASE)
# Create your views here.


class UploadMeasurmentsSet(viewsets.ViewSet):

    parser_classes = [MultiPartParser, FormParser]
    print("🚀 ~ UploadMeasurment class")

    def list(self, request):
        print("🚀 ~ UploadMeasurment List")
        reliabilityData = UploadReliabilityMeasurmentModel.objects.all()
        writeLatencyData = UploadWriteLatencyMeasurmentModel.objects.all()
        readLatencyData = UploadReadLatencyMeasurmentModel.objects.all()
        rowHammeringData = UploadRowHammeringMeasurmentModel.objects.all()

        reliability_serializer = UploadReliabilityMeasurmentModelSerializer(
            reliabilityData, many=True)
        writeLatency_serializer = UploadWriteLatencyMeasurmentModelSerializer(
            writeLatencyData, many=True)
        readLatency_serializer = UploadReadLatencyMeasurmentModelSerializer(
            readLatencyData, many=True)
        rowHammering_serializer = UploadRowHammeringMeasurmentModelSerializer(
            rowHammeringData, many=True)

        uploaded_measurments_data = {
            'reliabilityData': reliability_serializer.data,
            'writeLatencyData': writeLatency_serializer.data,
            'readLatencyData': readLatency_serializer.data,
            'rowHammeringData': rowHammering_serializer.data
        }
        return Response(uploaded_measurments_data)

    def create(self, request):
        print("🚀 ~ file: views.py:192 ~ request.data:", request.data)
        testType = request.data.get('testType')

        match = regex_pattern.search(testType)

        if match:
            print(match.group(1))
            if match.group(1).lower() == 'read'.lower():
                serializer = UploadReadLatencyMeasurmentModelSerializer(
                    data=request.data)
            elif match.group(1).lower() == 'write'.lower():
                serializer = UploadWriteLatencyMeasurmentModelSerializer(
                    data=request.data)
            elif match.group(1).lower() == 'reliability'.lower():
                serializer = UploadReliabilityMeasurmentModelSerializer(
                    data=request.data)
            elif match.group(1).lower() == 'row hammering'.lower():
                serializer = UploadRowHammeringMeasurmentModelSerializer(
                    data=request.data)
            else:
                return Response({'message': 'Invalid Test'}, status=400)

        print("is valid schema? ", serializer.is_valid())

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    '''def retrieve(self, request, pk=None):
        queryset = UploadMeasurments.objects.all()
        test = get_object_or_404(queryset, pk=pk)
        serializer = TestsSerializer(test)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        test = Tests.objects.get(pk=pk)
        serializer = TestsSerializer(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        test = Tests.objects.get(pk=pk)
        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)'''
