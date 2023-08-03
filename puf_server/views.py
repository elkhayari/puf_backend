from django.shortcuts import render
from rest_framework.response import Response
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
import math
import json
import csv
from pprint import pprint
import pandas as pd
from .models import Post
import numpy as np
import queue
import statistics
import time
import re
from django.utils import timezone
from tabulate import tabulate


# from .serialUSB import UartInterface
from .uart_communication_protocol import uart_serial, receive
from .uart_communication_protocol.command import Command, data2str, str2data
from .uart_communication_protocol.uart_frame_protocol import Frame
from .uart_communication_protocol.receive import Receive
from .uart_communication_protocol.uart_serial import UartInterface

from .uart_communication_protocol.connect_devices import SerialCommunication

from django.http import JsonResponse, HttpResponse

import redis
import threading
import os

# Models
from .models import Tests, TestOperations, Experiments
from .serializers import TestsSerializer, PostSerializer, TestOperationsSerializers, ExperimentsSerializers
from tests.models import ReliabilityMeasurmentTestsModel, ReadLatencyMeasurmentTestsModel, WriteLatencyMeasurmentTestsModel, RowHammeringMeasurmentTestsModel
from tests.serializers import ReliabilityMeasurmentTestsModelSerializer, ReadLatencyMeasurmentTestsModelSerializer, WriteLatencyMeasurmentTestsModelSerializer, RowHammeringMeasurmentTestsModelSerializer

import io
import seaborn as sns
import matplotlib.pyplot as plt

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .utils.PUFProcessor import PUFProcessor

READING = "READING"
WRITING = "WRITING"
END_WRITING = "END WRITING"
END_READING = "END READING"
FINISH = "FINISH"

# connectedDevices = SerialCommunication()

pool = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
redis = redis.Redis(connection_pool=pool)


def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))


regex_pattern = re.compile(
    r'(read|write|row hammering|reliability).+', re.IGNORECASE)


class PostView(APIView):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        print(request.data)
        posts_serializer = PostSerializer(data=request.data, many=True)
        if posts_serializer.is_valid():
            print("Before .save()")
            posts_serializer.save()
            print("After .save()")
            return Response(posts_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', posts_serializer.errors)
            return Response(posts_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# TODO delete this class after double check


class TestViewSet(viewsets.ViewSet):

    def list(self, request):
        tests = Tests.objects.all()
        serializer = TestsSerializer(tests, many=True)
        return Response(serializer.data)


class TestViewOperationsSet(viewsets.ViewSet):

    def list(self, request):
        print('LIST OF TEST OPERATION:')
        testsOP = TestOperations.objects.all()
        serializer = TestOperationsSerializers(testsOP, many=True)
        return Response(serializer.data)

    def create(self, request):
        print("CREATE A TEST OPERATION:")
        print('add an operation', request.data)
        serializer = TestOperationsSerializers(data=request.data)
        print('is_valide', serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        print('RETRIEVE A TEST OPERATIO:')
        queryset = TestOperations.objects.all()
        testOp = get_object_or_404(queryset, pk=pk)
        serializer = TestOperationsSerializers(testOp)
        return Response(serializer.data)

    def update(self, request, pk=None):
        print("UPDATE TEST OPERATION:")
        test = TestOperations.objects.get(pk=pk)
        serializer = TestOperationsSerializers(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        print('- DELETE a TEST OPERATION')
        testOp = TestOperations.objects.get(pk=pk)
        testOp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExperimentsSet(viewsets.ViewSet):

    def list(self, request):
        print('LIST OF Experiments:')
        experiments = Experiments.objects.all()
        serializer = ExperimentsSerializers(experiments, many=True)
        return Response(serializer.data)

    def create(self, request):
        print("CREATE an experiment:")
        print('add an operation', request.data)
        serializer = ExperimentsSerializers(data=request.data)
        print('is_valide', serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    '''def retrieve(self, request, pk=None):
        print('RETRIEVE A TEST OPERATIO:')
        queryset = TestOperations.objects.all()
        testOp = get_object_or_404(queryset, pk=pk)
        serializer = TestOperationsSerializers(testOp)
        return Response(serializer.data)

    def update(self, request, pk=None):
        print("UPDATE TEST OPERATION:")
        test = TestOperations.objects.get(pk=pk)
        serializer = TestOperationsSerializers(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        print('- DELETE a TEST OPERATION')
        testOp = TestOperations.objects.get(pk=pk)
        testOp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) '''

# TODO : create an api 'EvaluationUploadSet' for uploaded measurments
# TODO add upload field = true.


@api_view(["GET"])  # DELETE: Depricated
def EvaluationSet(request):
    # TODO : add file path
    # TODO : fetch test_mesurments and upload field to false.

    testsOP = TestOperations.objects.all()

    # Extract the IDs of the Child objects from the queryset
    testsOp_serializer = TestOperationsSerializers(testsOP, many=True)
    testOP_ids = [testOp.testId.id for testOp in testsOP]

    # Query Child objects using the extracted child IDs
    tests = Tests.objects.filter(id__in=testOP_ids)
    tests_serializer = TestsSerializer(tests, many=True)

    # If no ModelA object is found, return an empty list
    if not tests:
        return []

    # Create a list of dictionaries with the relevant data from both models
    evaluation_list = []
    for testOp in testsOp_serializer.data:
        for test in tests_serializer.data:
            if testOp['testId'] == test['id'] and testOp['status'] == "completed":
                evaluation_list.append({
                    'id': testOp['id'],
                    'created': testOp['createdAt'],
                    'fileName': testOp['fileName'],
                    'testTitle': test['title'],
                    'testType': test['testType'],
                    'memory': test['memory'],
                    'dataSetupTime': testOp['dataSetupTime'],
                    'iteration': testOp['iteration'],
                })

    return Response(evaluation_list)


def updateTestOp(updatedData, testType, pk=None):
    print('updateTestOp')
    print(updatedData)
    print(testType)
    print()
    match = regex_pattern.search(testType)

    if match:
        print(match.group(1))
        if match.group(1).lower() == 'read'.lower():
            measurmentTest = ReadLatencyMeasurmentTestsModel.objects.get(pk=pk)
            print(measurmentTest)
            serializer = ReadLatencyMeasurmentTestsModelSerializer(
                instance=measurmentTest, data=updatedData, partial=True)
            print(serializer)
        elif match.group(1).lower() == 'write'.lower():
            measurmentTest = WriteLatencyMeasurmentTestsModel.objects.get(
                pk=pk)
            serializer = WriteLatencyMeasurmentTestsModelSerializer(
                measurmentTest, data=updatedData)
        elif match.group(1).lower() == 'reliability'.lower():
            measurmentTest = ReliabilityMeasurmentTestsModel.objects.get(pk=pk)
            serializer = ReliabilityMeasurmentTestsModelSerializer(
                measurmentTest, data=updatedData)
        elif match.group(1).lower() == 'row hammering'.lower():
            measurmentTest = RowHammeringMeasurmentTestsModel.objects.get(
                pk=pk)
            serializer = RowHammeringMeasurmentTestsModelSerializer(
                measurmentTest, data=updatedData)
        else:
            return Response({'message': 'Invalid Test'}, status=400)

    print('is_valide', serializer.is_valid())
    if serializer.is_valid():
        serializer.save()


def getTestById(pk=None):
    print('Retrieve BY ID')
    queryset = Tests.objects.all()
    test = get_object_or_404(queryset, pk=pk)
    serializer = TestsSerializer(test)
    return serializer.data


@api_view(["GET"])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/test/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of test'
        },
        {
            'Endpoint': '/test/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single test object'
        },
        {
            'Endpoint': '/tests/create/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Creates new test with data sent in post request'
        },
        {
            'Endpoint': '/tests/id/update/',
            'method': 'PUT',
            'body': {'body': ""},
            'description': 'Creates an existing test with data sent in post request'
        },
        {
            'Endpoint': '/tests/id/delete/',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes and exiting test'
        },
    ]
    return Response(routes)

##########
# /errorPage or command not found


def errorPage(request):
    print('\033[93m> Devices \033[00m')
    print(str2data("Nothing"))
    result_command = Command.build_result_command()
    print("result {}".format(result_command.raw))
    uart.write(result_command.raw)
    received_frame = receive.receive_frame()
    print(received_frame)
    payload = data2str(received_frame.data)
    data = [{
        'payload': payload,
    }]
    return JsonResponse(data, safe=False)


def returnState(request):
    state = redis.get("stm32:state")
    data = {"state": state}
    return JsonResponse(data, safe=False)

##########
# /wrfram
##########


@csrf_exempt
@api_view(["POST"])
def writeReadToMem(request):
    prGreen("###################")
    prGreen("# WriteReadToMem #")
    prGreen("###################")

    print(request.data)
    thread = threading.Thread(
        target=multiple_clients_requests, args=(request,))
    try:
        thread.start()
    except:
        redis.set("stm32:state", "open")

    data = {"threadState": "started"}
    return JsonResponse(data, safe=False)


def getDevice(request):
    print('\033[93m> /getDevice  \033[00m')
    global connectedDevices
    connectedDevices = SerialCommunication()
    attempts = 0
    rem_frames = []
    receive_instance = receive.Receive(connectedDevices.uart_instances[0])

    idn_command = Command.build_idn_command()
    connectedDevices.uart_instances[0].write(idn_command.raw)

    received_frame, rem_frames = receive_instance.receive_frame(
        attempts, rem_frames)
    # TODO retrieve the instance from the payload/request
    print(received_frame)
    received_frame = Frame(received_frame[0])

    payload = data2str(received_frame.data)

    print('\033[93m>> Payload  \033[00m')
    print(f"{payload} \n")

    if received_frame.data == []:
        data = [{
            'id': 'seril',
            'name': 'name',
            'owner': 'default',
            'ExternalMemory': 'externalMemory',
            'is_ctive': False,
        }]
    else:
        res = json.loads(payload)
        data = [{
            'id': res['serial'],
            'name': res['name'],
            'owner': res['owner'],
            'ExternalMemory': 'default',
            'is_ctive': True,
        }]
    return JsonResponse(data, safe=False)


def multiple_clients_requests(request):
    print("🚀 ~ file: views.py:359 ~ request.data:", request.data)
    start_time = time.time()
    # TODO add try catch finally == state = open
    # redis.set("stm32:state", "busy")
    # TODO to be deleted
    testData = request.data.get('testData')
    memoryData = request.data.get('memoryData')
    deviceData = request.data.get('deviceData')

    redis.set("stm32:state", "open")
    prGreen(">> In multiple_clients")

    # Create a new queue
    test_queue = queue.Queue()

    for iteration in range(1):
        prGreen(f">> Iteration {iteration}")
        dataSetupTime_list = [
            dst for dst in testData["dataSetupTime"].split('-')]

        start_dst = int(dataSetupTime_list[0])
        stop_dst = int(dataSetupTime_list[-1]) - 1

        dataSetupTimes_range = [d for d in range(start_dst, stop_dst, -1)]
        print(dataSetupTimes_range)

        for dst in dataSetupTimes_range:
            data = {"testId": testData["id"],
                    "startedBy": "Anonymous_user",
                    "dataSetupTime": dst,
                    "status": "waiting",
                    "usedBy": "User_1",
                    "iteration": iteration,
                    "memoryType": memoryData["memoryType"],
                    "memoryBrand": memoryData["memoryBrand"],
                    "memoryModel": memoryData["memoryModel"],
                    "memoryLabel": memoryData["memoryLabel"],
                    "boardLabel": deviceData["device_label"],
                    "boardSerial": deviceData["serial_number"],
                    "boardName": deviceData["device_name"],
                    }

            testType = testData['testType']

            match = regex_pattern.search(testType)

            if match:
                print(match.group(1))
                if match.group(1).lower() == 'read'.lower():
                    serializer = ReadLatencyMeasurmentTestsModelSerializer(
                        data=data)
                elif match.group(1).lower() == 'write'.lower():
                    serializer = WriteLatencyMeasurmentTestsModelSerializer(
                        data=data)
                elif match.group(1).lower() == 'reliability'.lower():
                    serializer = ReliabilityMeasurmentTestsModelSerializer(
                        data=data)
                elif match.group(1).lower() == 'row hammering'.lower():
                    serializer = RowHammeringMeasurmentTestsModelSerializer(
                        data=data)
                else:
                    return Response({'message': 'Invalid Test'}, status=400)

            print('is_valide', serializer.is_valid())
            if serializer.is_valid():
                serializer.save()
                data_test = serializer.data

            test_queue.put(data_test)

        while not test_queue.empty():
            currentRunningTest = test_queue.get()
            print(currentRunningTest)
            prYellow(
                f">> Running test: dst = {currentRunningTest['dataSetupTime']} Iteration {currentRunningTest['iteration']}")
            startTest(currentRunningTest, testData, deviceData)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"***************************************")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print(f"***************************************")
    redis.set("stm32:state", "open")


def startTest(currentRunningTest, testData, deviceData):
    # Add a test operation.##########################
    print()
    prYellow(f">>> measurment: {currentRunningTest}")
    prGreen(f">>> data: {testData}")
    print('---')

    currentRunningTest["status"] = "running"
    # currentRunningTest["startedAt"] = timezone.now
    testType = testData["testType"]

    updateTestOp(currentRunningTest, testType, currentRunningTest["id"])

    print('- AFTER UPDATE --')

    prYellow(f">> test: {currentRunningTest}")
    print('---')
    prGreen(f">>> data: {testData}")
    print()

    ##################################################

    print('\n\033[93m*** WRITE READ TO FRAM MEMORY *** \033[00m\n')
    # add a try catch in order to return an error
    # receive_instance = receive.Receive(connectedDevices.uart_instances[0])
    uart_instance = UartInterface(deviceData['device_port'])
    receive_instance = Receive(uart_instance)

    json_payload = get_test_payload(testData, currentRunningTest)
    pprint(json_payload)

    # write_read_command = Command.build_custom_payload(currentRunningTest["dataSetupTime"])
    write_read_command = Command.build_custom_payload(json_payload)
    print("wrf command {}".format(write_read_command.raw))

    # TODO fetch the device instance from request.data
    uart_instance.write(write_read_command.raw)

    attempts = 0
    rem_frames = []
    # received_frames, rem_frames = receive.receive_frame(attempts, [])
    print("received frame in wrfram()")

    ''' loop over a list of frames
        each frame start with 171 
        205 means that the board sends state/message
        239 a read value
        end flags are: 225, 226
    '''
    counter = 0

    redis.set("testOperation:"+str(currentRunningTest["id"])+":progress", 0)
    redis.set("stm32:fram:test0:state", "START")
    prGreen(">>> {}".format(redis.get("stm32:fram:test0:state")))
    print("stm in {} mode...".format(redis.get("stm32:fram:test0:state")))

    values = []
    while redis.get("stm32:fram:test0:state") != FINISH:
        test_status = redis.get("stm32:fram:test0:state")
        prYellow(f">>> Attempt {attempts+1} {test_status}")
        if attempts > 1 and test_status == "START":
            uart_instance.write(write_read_command.raw)
        received_frames, rem_frames = receive_instance.receive_frame(
            attempts, rem_frames)
        for raw in received_frames:
            single_frame = Frame(raw)
            if single_frame.raw[1] == 205:
                prGreen("State changed to {}".format(
                    data2str(single_frame.data)))
                redis.set("stm32:fram:test0:state",
                          data2str(single_frame.data))

            elif single_frame.raw[1] == 239:
                counter += 1
                prGreen(raw)
                values.append(single_frame.raw[3])
                if counter % 100 == 0:
                    print(f"counter == {counter}")

            else:
                print("flag not recognized")

        attempts += 1

    redis.set("testOperation:"+str(currentRunningTest["id"])+":progress", 100)

    prGreen("> Done with  {} state <".format(
        redis.get("stm32:fram:test0:state")))

    redis.set("stm32:state", "open")

    currentRunningTest["status"] = "completed"

    updateTestOp(currentRunningTest, testType, currentRunningTest["id"])

    time.sleep(2)

    file_name = "memory-yZy" + \
        str(currentRunningTest['memoryLabel']) + "_" + str(currentRunningTest['memoryModel']) + str(testData['voltage']) + \
        "V-" + "_dst-" + \
        str(currentRunningTest['dataSetupTime']) + \
        "_" + str(currentRunningTest['id']) + "_" + \
        str(currentRunningTest['iteration'])

    save_data_csv(["Address", "Value"], values, file_name, testType,
                  currentRunningTest)


def get_test_payload(testData, currentRunningTest):

    match = regex_pattern.search(testData['testType'])
    print(match.group(1))

    # If a match is found, set the testType accordingly
    if match:
        if match.group(1).lower() == "reliability":
            testType = "reliabilityTest"
        elif match.group(1).lower() == "read":
            testType = "readLatencyTest"
        elif match.group(1).lower() == "write":
            testType = "writeLatencyTest"
        elif match.group(1).lower() == "row hammering":
            testType = "rowHammingTest"
        else:
            testType = "notDefined"

    payload = {
        "HEADER": "TEST",
        "paramsSize": 0,
        "testType": testType,
        "initialValue": testData["initialValue"],
        "startAddress": testData["startAddress"],
        "stopAddress": testData["stopAddress"],
        "dataSetupTime": currentRunningTest["dataSetupTime"]
    }

    # convert the dictionary to a JSON string and return
    return json.dumps(payload)


def split_list_into_matrix_carry(my_list, cols, default=None):
    rows = math.ceil(len(my_list) / cols)
    print("cols", cols)
    matrix = []

    for i in range(cols):
        row = my_list[i * cols: (i + 1) * cols] + [default] * \
            (cols - len(my_list[i * cols: (i + 1) * cols]))
        matrix.append(row)

    return matrix


def save_data_csv(header, values, file_name, testType, currentRunningTest):
    # current_directory = os.getcwd()
    file_path = os.path.join("assets/csv_files", file_name+".csv")

    # Open the CSV file for writing
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the data to the CSV file
        writer.writerow(header)
        for address, item in enumerate(values):
            row = [hex(address), hex(item)]
            writer.writerow(row)

    currentRunningTest["fileName"] = file_path
    updateTestOp(currentRunningTest, testType, currentRunningTest["id"])

    prGreen("----------------------")
    prGreen(">>> CSV FILE SAVED <<<")
    prGreen("----------------------")


@api_view(["POST"])
def getHeatmap(request):
    # Return the image file as an HTTP response
    print("-----getHeatMap------")
    print(request.data)
    print("-----------")

    csv_files = [item["fileName"] for item in request.data]
    # all_data = pd.concat([pd.read_csv(f) for f in csv_files])
    tests_id_list = [item["id"] for item in request.data]
    id_string = "_".join([str(tests_id_list[0]), str(tests_id_list[-1])])
    # print(test_ids)

    file_name = "memory_FRAM_12.0V-xxx_" + id_string
    print(file_name)
    # Name of the column to generate the heatmap for
    # column_name = 'Value'

    # Create a list of lists with some data
    # values = all_data[column_name].tolist()
    for i, file in enumerate(csv_files):
        if i == 0:
            values = pd.read_csv(file)['Value'].tolist()

        else:
            new_values = pd.read_csv(file)['Value'].tolist()
            values = [int(x == y) for x, y in zip(values, new_values)]
    print(values)
    row_len = int(math.sqrt(len(values)))
    matrix = split_list_into_matrix_carry(values, row_len, 0)
    # print(row_len)
    # print(len(matrix))
    print(matrix)

    # Create a heatmap using Seaborn
    #
    sns.heatmap(matrix,  cmap='hot',  fmt='.2f')
    # cbar = ax.collections[0].colorbar
    # cbar.set_label('Value')
    # Define the custom color palette
    '''colors = [(1.0, 1.0, 1.0), (0.0, 0.0, 0.0)]  # white and black
    cmap = sns.color_palette(colors)

    #   Create the heatmap
    ax = sns.heatmap(values, cmap=cmap, cbar=False,
                     square=True, annot=True, fmt='.0f')

    # Set the ticks and labels
    ax.set_xticks(np.arange(values.shape[0]) + 0.5)
    ax.set_xticklabels(np.arange(1, values.shape[0] + 1))
    ax.set_yticks(np.arange(values.shape[1]) + 0.5)
    ax.set_yticklabels(np.arange(1, values.shape[1] + 1))

    # Add the legend
    legend = ax.legend(title="Value", labels=[
                       "0", "1"], loc="bottom", ncol=2, bbox_to_anchor=(0.5, -0.2), frameon=False)
    for i, text in enumerate(legend.get_texts()):
        text.set_color(colors[i]) '''

    # Save the plot as an image to a file
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Create a new file object in memory from the saved image file
    file = ContentFile(buffer.read())

    # Save the image file to the default storage location
    file_name_png = file_name + '.png'
    path = default_storage.save(file_name_png, file)

    # data["fileName"] = file_name_png
    # updateTestOp(data, testOpId)
    path = os.path.join(settings.MEDIA_ROOT, file_name_png)

    with default_storage.open(path) as f:
        response = HttpResponse(f.read(), content_type='image/png')
        # response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# other metrics


# @api_view(["POST"])
def getMetrics(data):
    def truncate_func(x): return x[:10] if isinstance(x, str) else x

    prGreen("------------------Get Metrics-----------------")

    # print(request.data)
    selectedMeasurments = data['measurments']
    uniformityChallengesKey = data['uniformityChallenges']
    robustnessChallengesKey = data['robustnessChallenges']
    uniquenessChallengesKey = data['uniquenessChallenges']

    data_df = pd.DataFrame(selectedMeasurments).reset_index(drop=True)
    # print(data_df)
    testType_group_keys = ["testType"]
    memory_group_keys = ["memoryType",
                         "memoryBrand", "memoryModel"]

    initialValue_group_keys = ["initialValue"]
    challenge_group_keys = ["dataSetupTime", "voltage"]  # Dynamic

    prGreen("-----------------UNIFORMITY--------------------")
    uniformity = []

    # Group the DataFrame by 'Memory Type'
    for testName, tests_group in data_df.groupby(testType_group_keys):
        # print(testName)
        testTypeObject = {}
        testTypeObject["testType"] = testName
        testTypeObject["memories"] = []

        for name, memory_group in tests_group.groupby(memory_group_keys):
            groupby_mem_key = '/'.join(str(item) for item in name)
            # prYellow(f"> Memory key: {groupby_mem_key}")
            memoryInstanceObject = {}
            memoryInstanceObject["memoryKey"] = groupby_mem_key
            memoryInstanceObject["initialValueKey"] = []

            for initialVallue_names, initialvalues_group in memory_group.groupby(initialValue_group_keys):
                # prYellow(f">> Initial value: {initialVallue_names}")

                initialValueObject = {}

                initialValueObject["initialValue"] = initialVallue_names
                initialValueObject["startStopAddresses"] = []

                for startStopAddress, group in initialvalues_group.groupby(["startAddress", "stopAddress"]):
                    key_address_group = '-'.join(str(item)
                                                 for item in startStopAddress)

                    # prYellow(f">>> Address key: {key_address_group}")

                    startStopAddressObject = {}
                    startStopAddressObject["startAddress"], startStopAddressObject["stopAddress"] = startStopAddress
                    startStopAddressObject["challengeKeys"] = uniformityChallengesKey
                    startStopAddressObject["challenges"] = []

                    for challengeNames, group_challenge in group.groupby(uniformityChallengesKey):
                        challengeObject = {}
                        challengeObject["challenge"] = []
                        if len(uniformityChallengesKey) > 1:
                            for index, challenge in enumerate(uniformityChallengesKey):
                                challengeObject["challenge"].append(
                                    {"challengeName": challenge, "challengeValue": challengeNames[index]})
                        else:
                            challengeObject["challenge"].append(
                                {"challengeName": uniformityChallengesKey[0], "challengeValue": challengeNames})

                        # print(challengeObject)
                        challengeObject["challenge_measuremenst"] = []

                        for index, row in group_challenge.iterrows():
                            chip_data = {}
                            chip_data = row.to_dict()

                            mem_response = PUFProcessor.read_and_store_input_data(
                                row.fileName, row.startAddress, row.stopAddress)

                            ones, zeros, gaps = PUFProcessor.calculate_ones_and_zeros(
                                mem_response)

                            fractional_hamming_weight = ones / (ones+zeros)

                            chip_data["hammingWeight"] = fractional_hamming_weight

                            chip_data["ones"], chip_data["zeros"], chip_data["gaps"] = ones, zeros, gaps

                            challengeObject["challenge_measuremenst"].append(
                                chip_data)

                        startStopAddressObject["challenges"].append(
                            challengeObject)

                    initialValueObject["startStopAddresses"].append(
                        startStopAddressObject)

                memoryInstanceObject["initialValueKey"].append(
                    initialValueObject)

            testTypeObject["memories"].append(memoryInstanceObject)

        uniformity.append(testTypeObject)

    # pprint(uniformity)

    data = [(item['id'], item["fileName"]) for item in selectedMeasurments]

    prGreen("-----------------ROBUSTNESS-------------------")

    intra_hd_list = []
    #####
    # Group the DataFrame by 'Memory Type'
    for testName, tests_group in data_df.groupby(testType_group_keys):
        # print(testName)
        testTypeObject = {}
        testTypeObject["testType"] = testName
        testTypeObject["memories"] = []

        for name, memory_group in tests_group.groupby(memory_group_keys):
            groupby_mem_key = '/'.join(str(item) for item in name)
            # prYellow(f"> Memory key: {groupby_mem_key}")
            memoryInstanceObject = {}
            memoryInstanceObject["memoryKey"] = groupby_mem_key
            memoryInstanceObject["initialValueKey"] = []

            for initialVallue_names, initialvalues_group in memory_group.groupby(initialValue_group_keys):
                # prYellow(f">> Initial value: {initialVallue_names}")

                initialValueObject = {}

                initialValueObject["initialValue"] = initialVallue_names
                initialValueObject["startStopAddresses"] = []

                for startStopAddress, group in initialvalues_group.groupby(["startAddress", "stopAddress"]):
                    key_address_group = '-'.join(str(item)
                                                 for item in startStopAddress)

                    # prYellow(f">>> Address key: {key_address_group}")

                    startStopAddressObject = {}
                    startStopAddressObject["startAddress"], startStopAddressObject["stopAddress"] = startStopAddress
                    startStopAddressObject["challengeKeys"] = robustnessChallengesKey
                    startStopAddressObject["chipInstances"] = []

                    for chip_name, group_chips in data_df.groupby("memoryLabel"):
                        key_chip_group = chip_name
                        # prYellow(key_chip_group)
                        # print(tabulate(group_chips))
                        chipObject = {}
                        chipObject["chipLabel"] = chip_name
                        chipObject["challenges"] = []

                        for challengeNames, group_challenge in group_chips.groupby(robustnessChallengesKey):
                            challengeObject = {}
                            challengeObject["challenge"] = []
                            if len(robustnessChallengesKey) > 1:
                                for index, challenge in enumerate(robustnessChallengesKey):
                                    challengeObject["challenge"].append(
                                        {"challengeName": challenge, "challengeValue": challengeNames[index]})
                            else:
                                challengeObject["challenge"].append(
                                    {"challengeName": robustnessChallengesKey[0], "challengeValue": challengeNames})

                            # print(challengeObject)
                            challengeObject["challenge_measuremenst"] = []
                            # print(tabulate(group_challenge))

                            # -#-#-#
                            hd_list_single_device_challenge = []
                            if len(group_challenge) > 1:
                                for row1 in group_challenge.itertuples(index=True):
                                    for row2 in group_challenge.loc[row1.Index+1:].itertuples(index=True):
                                        puf_response_1 = PUFProcessor.read_and_store_input_data(
                                            row1.fileName, row1.startAddress, row1.stopAddress)
                                        puf_response_2 = PUFProcessor.read_and_store_input_data(
                                            row2.fileName, row2.startAddress, row2.stopAddress)
                                        # print(len(puf_response_1))
                                        # print(len(puf_response_2))
                                        if len(puf_response_1) == len(puf_response_2):
                                            hd_list_single_device_challenge.append(
                                                PUFProcessor.hamming_distance(puf_response_1, puf_response_2))

                                # print(hd_list_single_device_challenge)
                                data = {"Robustness": True,
                                        "hammingDistance": {
                                            "min": min(hd_list_single_device_challenge),
                                            "max": max(hd_list_single_device_challenge),
                                            "avg": statistics.mean(hd_list_single_device_challenge)
                                        }}
                                # chip_measurements.append(data)

                            else:
                                data = {"Robustness": False,
                                        }

                            challengeObject["challenge_measuremenst"].append(
                                data)

                            chipObject["challenges"].append(challengeObject)

                        startStopAddressObject["chipInstances"].append(
                            chipObject)

                    initialValueObject["startStopAddresses"].append(
                        startStopAddressObject)

                memoryInstanceObject["initialValueKey"].append(
                    initialValueObject)

            testTypeObject["memories"].append(memoryInstanceObject)

        intra_hd_list.append(testTypeObject)

    # pprint(intra_hd_list)

    prGreen("----------------------------------------------")
    prGreen("-----------------Uniqueness-------------------")
    prGreen("----------------------------------------------")

    dataframes = {}
    uniqueness_data = []

    prGreen("> Instances")

    for testName, tests_group in data_df.groupby(testType_group_keys):
        # print(testName)
        testTypeObject = {}
        testTypeObject["testType"] = testName
        testTypeObject["memories"] = []

        if len(tests_group) > 1:
            # print(tabulate(tests_group))
            grouped_by_memory = tests_group.groupby(memory_group_keys)
            for name, memory_group in grouped_by_memory:
                key_group = '/'.join(str(item) for item in name)
                # prYellow(f"name - {key_group}")
                # print(tabulate(memory_group, headers='keys', tablefmt='psql'))
                dataframes[key_group] = memory_group.copy()

            # Iterate over each group and create a dataframe for each group
            for groupby_mem_key in dataframes:
                # prYellow(f"> Memory key: {groupby_mem_key}")
                instanceData = {}
                # GroupBy start & stop adrress
                # Iterate over each group
                instanceData["memoryKey"] = groupby_mem_key
                instanceData["initialValueKey"] = []

                for initialVallue_names, initialvalues_group in dataframes[groupby_mem_key].groupby(initialValue_group_keys):
                    # prYellow(f"> Initial value: {initialVallue_names}")
                    # print(tabulate(initialvalues_group))
                    initialvalueObject = {}

                    initialvalueObject["initialValue"] = initialVallue_names

                    initialvalueObject["startStopAddresses"] = []
                    for startStopAddress, group in dataframes[groupby_mem_key].groupby(["startAddress", "stopAddress"]):
                        key_address_group = '-'.join(str(item)
                                                     for item in startStopAddress)

                        # prYellow(f">> Address key: {key_address_group}")
                        # print(tabulate(group.applymap(truncate_func),
                        # headers='keys', tablefmt='psql'))

                        # GroupBy challenges
                        # Iterate over each group
                        startStopAddressObject = {}
                        startStopAddressObject["startAddress"], startStopAddressObject["stopAddress"] = startStopAddress
                        startStopAddressObject["challenges"] = []
                        for j, group_challenge in group.groupby(challenge_group_keys):
                            if isinstance(j, tuple):
                                key_challenge_group = '-'.join(str(item)
                                                               for item in j)
                            else:
                                key_challenge_group = j

                            # prYellow(
                                # f">>> challenge key {key_challenge_group}")

                            challengeObject = {}
                            challengeObject["challenge"] = key_challenge_group
                            challengeObject["inter_hamming_distances"] = []
                            if len(group_challenge) > 1:
                                # print(tabulate(group_challenge.applymap(
                                # truncate_func), headers='keys', tablefmt='psql'))
                                # TODO: calculate uniqueness
                                # prGreen(
                                # '################## LOGIC #######################\n')

                                for measurment_1 in group_challenge.itertuples(index=True):
                                    for measurment_2 in group_challenge.loc[measurment_1.Index+1:].itertuples(index=True):
                                        # prGreen(f"{measurment_1}")
                                        # print('vs')
                                        # prGreen(f"{measurment_2}")

                                        puf_response_1 = PUFProcessor.read_and_store_input_data(
                                            measurment_1.fileName, measurment_1.startAddress, measurment_1.stopAddress)
                                        # print(puf_response_1)
                                        puf_response_2 = PUFProcessor.read_and_store_input_data(
                                            measurment_2.fileName, measurment_2.startAddress, measurment_2.stopAddress)
                                        # print(puf_response_1)
                                        # print(puf_response_2)
                                        hamming_distance = PUFProcessor.hamming_distance(
                                            puf_response_1, puf_response_2)
                                        # prGreen(hamming_distance)
                                        inter_hamming_distance = {"chip1": measurment_1.memoryLabel,
                                                                  "iterationChip1": measurment_1.iteration,
                                                                  "chip2": measurment_2.memoryLabel,
                                                                  "iterationChip2": measurment_2.iteration,
                                                                  "hammingDistance": hamming_distance}
                                        challengeObject["inter_hamming_distances"].append(
                                            inter_hamming_distance)
                                # prGreen(
                                    # '\n################################################\n')
                                challengeObject["min_inter_hamming_distances"] = 0
                                challengeObject["max_inter_hamming_distances"] = 0
                                challengeObject["avg_inter_hamming_distances"] = 0
                            else:
                                prYellow("!! No Data For This challenge")

                            startStopAddressObject["challenges"].append(
                                challengeObject)
                        # prGreen('DONE memory gr')
                        initialvalueObject["startStopAddresses"].append(
                            startStopAddressObject)

                    # uniqueness_data.append(initialvalueObject)
                    instanceData["initialValueKey"].append(initialvalueObject)

                testTypeObject["memories"].append(instanceData)
                prYellow("---------------------------------------------")
        uniqueness_data.append(testTypeObject)
        # print('######')
        # pprint(uniqueness_data)
    # Create a list of lists with some data
    evaluation_list = []

    evaluation_list.append({
        'uniformity': uniformity,
        'intra_hd_list': intra_hd_list,
        'inter_hd_list': uniqueness_data
    })

    return {
        "uniformity": uniformity,
        "intra_hd_list": intra_hd_list,
        "inter_hd_list": uniqueness_data
    }


@api_view(["GET"])
def getImage(request, file_name):
    # Return the image file as an HTTP response
    print("-----------")
    print(file_name)
    print("-----------")
    path = os.path.join(settings.MEDIA_ROOT, file_name)

    with default_storage.open(path) as f:
        response = HttpResponse(f.read(), content_type='image/png')
        # response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


def progress(request):
    # Calculate the progress based on the time elapsed
    # Assuming the sleep operation takes 5 seconds
    print('progress')
    elapsed_time = 5
    progress = int((elapsed_time / 5) * 100)

    return JsonResponse({'progress': progress})
