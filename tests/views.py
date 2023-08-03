from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.http import JsonResponse

import re

from .models import ReliabilityTestsModel, WriteLatencyTestsModel, ReadLatencyTestsModel, RowHammeringTestsModel, ReliabilityMeasurmentTestsModel, ReadLatencyMeasurmentTestsModel, WriteLatencyMeasurmentTestsModel, RowHammeringMeasurmentTestsModel
from .serializers import ReadLatencyTestsModelSerializer, ReliabilityTestsModelSerializer, WriteLatencyTestsModelSerializer, RowHammeringTestsModelSerializer, ReadLatencyMeasurmentTestsModelSerializer, ReliabilityMeasurmentTestsModelSerializer, WriteLatencyMeasurmentTestsModelSerializer, RowHammeringMeasurmentTestsModelSerializer


regex_pattern = re.compile(
    r'(read|write|row hammering|reliability).*', re.IGNORECASE)

# Create your views here.


class TestViewSet(viewsets.ViewSet):
    print("HEllo from tests app")

    def list(self, request):

        reliabilityData = ReliabilityTestsModel.objects.all()
        writeLatencyData = WriteLatencyTestsModel.objects.all()
        readLatencyData = ReadLatencyTestsModel.objects.all()
        rowHammeringData = RowHammeringTestsModel.objects.all()

        reliability_serializer = ReliabilityTestsModelSerializer(
            reliabilityData, many=True)
        writeLatency_serializer = WriteLatencyTestsModelSerializer(
            writeLatencyData, many=True)
        readLatency_serializer = ReadLatencyTestsModelSerializer(
            readLatencyData, many=True)
        rowHammering_serializer = RowHammeringTestsModelSerializer(
            rowHammeringData, many=True)

        uploaded_measurments_data = {
            'reliabilityData': reliability_serializer.data,
            'writeLatencyData': writeLatency_serializer.data,
            'readLatencyData': readLatency_serializer.data,
            'rowHammeringData': rowHammering_serializer.data
        }
        return Response(uploaded_measurments_data)

    def create(self, request):
        # serializer = TestsSerializer(data=request.data)
        print("🚀 ~ file: views.py:192 ~ request.data:", request.data)
        testType = request.data.get('testType')

        match = regex_pattern.search(testType)

        if match:
            if match.group(1).lower() == 'read'.lower():
                serializer = ReadLatencyTestsModelSerializer(
                    data=request.data)
            elif match.group(1).lower() == 'write'.lower():
                serializer = WriteLatencyTestsModelSerializer(
                    data=request.data)
            elif match.group(1).lower() == 'reliability'.lower():
                serializer = ReliabilityTestsModelSerializer(
                    data=request.data)
            elif match.group(1).lower() == 'row hammering'.lower():
                serializer = RowHammeringTestsModelSerializer(
                    data=request.data)
            else:
                return Response({'message': 'Invalid Test'}, status=400)

        print("is valid schema? ", serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        print(request.data.get('testType'))

        # queryset = Tests.objects.all()
        # test = get_object_or_404(queryset, pk=pk)
        # serializer = TestsSerializer(test)
        # return Response(serializer.data)

    def update(self, request, pk=None):
        testType = request.data.get('testType')
        match = regex_pattern.search(testType)

        if match:
            print("match")
            print(match.group(1))
            if match.group(1).lower() == 'read'.lower():
                test = ReadLatencyTestsModel.objects.get(pk=pk)
                serializer = ReadLatencyTestsModelSerializer(
                    test, data=request.data)
            elif match.group(1).lower() == 'write'.lower():
                test = WriteLatencyTestsModel.objects.get(pk=pk)
                serializer = WriteLatencyTestsModelSerializer(
                    test, data=request.data)
            elif match.group(1).lower() == 'reliability'.lower():
                test = ReliabilityTestsModel.objects.get(pk=pk)
                serializer = ReliabilityTestsModelSerializer(
                    test, data=request.data)
            elif match.group(1).lower() == 'row hammering'.lower():
                test = RowHammeringTestsModel.objects.get(pk=pk)
                serializer = RowHammeringTestsModelSerializer(
                    test, data=request.data)
            else:
                return Response({'message': 'Invalid Test'}, status=400)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        print("🚀 ~ destroy: views.py:192 ~ request.data:", request.data)
        testType = request.data.get('testType')

        match = regex_pattern.search(testType)

        if match:
            print("match")
            print(match.group(1))
            if match.group(1).lower() == 'read'.lower():
                test = ReadLatencyTestsModel.objects.get(pk=pk)
            elif match.group(1).lower() == 'write'.lower():
                test = WriteLatencyTestsModel.objects.get(pk=pk)
            elif match.group(1).lower() == 'reliability'.lower():
                test = ReliabilityTestsModel.objects.get(pk=pk)
            elif match.group(1).lower() == 'row hammering'.lower():
                test = RowHammeringTestsModel.objects.get(pk=pk)
            else:
                return Response({'message': 'Invalid Test'}, status=400)

        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_measurments_by_status(status):
    Reliability_querysets = ReliabilityMeasurmentTestsModel.objects.filter(
        status=status).select_related("testId").all()
    WriteLatency_querysets = WriteLatencyMeasurmentTestsModel.objects.filter(
        status=status).select_related("testId").all()
    readLatency_querysets = ReadLatencyMeasurmentTestsModel.objects.filter(
        status=status).select_related("testId").all()
    RowHammering_querysets = RowHammeringMeasurmentTestsModel.objects.filter(
        status=status).select_related("testId").all()

    readLatency_measurments = []
    writeLatency_measurments = []
    reliability_measurments = []
    rowHammering_measurments = []

    for queryset in readLatency_querysets:
        readLatency_serializer = ReadLatencyMeasurmentTestsModelSerializer(
            queryset)

        serilized_data = readLatency_serializer.data
        additional_data = {
            'initialValue': queryset.testId.initialValue,
            'testType': queryset.testId.testType,
            'startAddress': queryset.testId.startAddress,
            'stopAddress': queryset.testId.stopAddress,
            'voltage': queryset.testId.voltage,
            'temperature': queryset.testId.temperature

        }

        serilized_data.update(additional_data)
        readLatency_measurments.append(serilized_data)

    for queryset in WriteLatency_querysets:
        writeLatency_serializer = WriteLatencyMeasurmentTestsModelSerializer(
            queryset)

        serilized_data = writeLatency_serializer.data
        additional_data = {
            'initialValue': queryset.testId.initialValue,
            'testType': queryset.testId.testType,
            'startAddress': queryset.testId.startAddress,
            'stopAddress': queryset.testId.stopAddress,
            'voltage': queryset.testId.voltage,
            'temperature': queryset.testId.temperature
        }

        serilized_data.update(additional_data)
        writeLatency_measurments.append(serilized_data)

    for queryset in Reliability_querysets:
        reliabilty_serializer = ReliabilityMeasurmentTestsModelSerializer(
            queryset)

        serilized_data = reliabilty_serializer.data
        additional_data = {
            'initialValue': queryset.testId.initialValue,
            'testType': queryset.testId.testType,
            'startAddress': queryset.testId.startAddress,
            'stopAddress': queryset.testId.stopAddress,
            'voltage': queryset.testId.voltage,
            'temperature': queryset.testId.temperature
        }

        serilized_data.update(additional_data)
        reliability_measurments.append(serilized_data)

    for queryset in RowHammering_querysets:
        rowHammering_serializer = RowHammeringMeasurmentTestsModelSerializer(
            queryset)

        serilized_data = rowHammering_serializer.data
        additional_data = {
            'initialValue': queryset.testId.initialValue,
            'testType': queryset.testId.testType,
            'startAddress': queryset.testId.startAddress,
            'stopAddress': queryset.testId.stopAddress,
            'voltage': queryset.testId.voltage,
            'temperature': queryset.testId.temperature
        }

        serilized_data.update(additional_data)
        rowHammering_measurments.append(serilized_data)

    measurments_status_data = {
        'reliabilityData': reliability_measurments,
        'writeLatencyData': writeLatency_measurments,
        'readLatencyData': readLatency_measurments,
        'rowHammeringData': rowHammering_measurments
    }

    return measurments_status_data


@api_view(["GET"])
def getRunningTests(request):
    filter_param = request.GET.get('filter')

    return JsonResponse(get_measurments_by_status(filter_param), safe=False)


@api_view(["GET"])
def EvaluationSet(request):
    evaluation_list = []

    evaluation_list.append(get_measurments_by_status("completed"))

    return Response(get_measurments_by_status("completed"))
