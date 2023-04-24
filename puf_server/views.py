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
import logging
from .models import Post
import numpy as np
import queue
import statistics
import time

#from .serialUSB import UartInterface
from .uart_communication_protocol import uart_serial, receive
from .uart_communication_protocol.command import Command, data2str, str2data
from .uart_communication_protocol.uart_frame_protocol import Frame

from .uart_communication_protocol.connect_devices import SerialCommunication

from django.http import JsonResponse, HttpResponse

import redis
import threading
import os
# Models
from .models import Tests, TestOperations, Image, Experiments
from .serializers import TestsSerializer, TestOperationsSerializers, ImageSerializers, ExperimentsSerializers

from django.core.files import File
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


connectedDevices = SerialCommunication()

pool = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
redis = redis.Redis(connection_pool=pool)


def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))


class TestViewSet(viewsets.ViewSet):

    def list(self, request):
        tests = Tests.objects.all()
        serializer = TestsSerializer(tests, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = TestsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = Tests.objects.all()
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
        return Response(status=status.HTTP_204_NO_CONTENT)


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


@api_view(["GET"])
def EvaluationSet(request):

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
                    'created': testOp['lastUse'],
                    'fileName': testOp['fileName'],
                    'testTitle': test['title'],
                    'testType': test['testType'],
                    'memory': test['memory'],
                    'dataSetupTime': testOp['dataSetupTime'],
                    'iteration': testOp['iteration'],
                })

    return Response(evaluation_list)


def updateTestOp(data, pk=None):
    testOp = TestOperations.objects.get(pk=pk)
    serializer = TestOperationsSerializers(testOp, data=data)
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

    received_frame, rem_frames = receive_instance.receive_frame(attempts, rem_frames)
    # TODO retrieve the instance from the payload/request
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
    # TODO add try catch finally == state = open
    #redis.set("stm32:state", "busy")
    # TODO to be deleted
    redis.set("stm32:state", "open")
    prGreen(">> In multiple_clients")

    # Create a new queue
    test_queue = queue.Queue()

    start_time = time.time()

    for iteration in range(1):
        prGreen(f">> Iteration {iteration}")
        dataSetupTime_list = [
        dst for dst in request.data["dataSetupTime"].split('-')]

        start_dst = int(dataSetupTime_list[0])
        stop_dst = int(dataSetupTime_list[-1]) - 1

        dataSetupTimes_range = [d for d in range(start_dst, stop_dst, -1)]
        print(dataSetupTimes_range)
        for dst in dataSetupTimes_range:
            data = {"testId": request.data["id"],
                    "dataSetupTime": dst,
                    "status": "waiting",
                    "usedBy": "User_1",
                    "iteration": iteration
                    }
            serializer = TestOperationsSerializers(data=data)
            print('is_valide', serializer.is_valid())
            if serializer.is_valid():
                serializer.save()
                data_test = serializer.data

            test_queue.put(data_test)

        while not test_queue.empty():
            currentRunningTest = test_queue.get()
            prYellow(f">> Running test: dst = {currentRunningTest['dataSetupTime']} Iteration {currentRunningTest['iteration']}")
            startTest(currentRunningTest, request.data)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"***************************************")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print(f"***************************************")

    
def startTest(currentRunningTest, data):
    # Add a test operation.##########################
    print()
    prYellow(f">>> test: {currentRunningTest}")
    print('---')
    prGreen(f">>> data: {data}")
    print()
    currentRunningTest["status"] = "running"

    updateTestOp(currentRunningTest, currentRunningTest["id"])

    print('- AFTER UPDATE --')

    prYellow(f">> test: {currentRunningTest}")
    print('---')
    prGreen(f">>> data: {data}")
    print()
    print(connectedDevices.uart_instances)

    ##################################################

    print('\n\033[93m*** WRITE READ TO FRAM MEMORY *** \033[00m\n')
    receive_instance = receive.Receive(connectedDevices.uart_instances[0])

    if data["testType"] == 'Read latency test':
        print(f'Read Latency Test with dst = {currentRunningTest["dataSetupTime"]}')
        payload = { "HEADER":"TEST",
                    "paramsSize":0,
                    "testType" : "readLatencyTest",
                    "initialValue": "0x55",
                    "startAddress": 0,
                    "stopAddress": 1,
                    "dataSetupTime": currentRunningTest["dataSetupTime"] }
        
        # convert the dictionary to a JSON string
        json_payload = json.dumps(payload)

        #write_read_command = Command.build_custom_payload(currentRunningTest["dataSetupTime"])
        write_read_command = Command.build_custom_payload(json_payload)
        print("wrf command {}".format(write_read_command.raw))

    else:
        # reliability tes
        write_read_command = Command.build_rwf_command()
        print("wrf command {}".format(write_read_command.raw))

    #TODO fetch the device instance from request.data
    connectedDevices.uart_instances[0].write(write_read_command.raw)

    attempts = 0
    rem_frames = []
    #received_frames, rem_frames = receive.receive_frame(attempts, [])
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
    #print("stm in {} mode...".format(redis.get("stm32:fram:test0:state")))

    values = []
    while redis.get("stm32:fram:test0:state") != FINISH:
        test_status = redis.get("stm32:fram:test0:state")
        prYellow(f">>> Attempt {attempts+1} {test_status}")
        if attempts > 1 and test_status == "START":
            connectedDevices.uart_instances[0].write(write_read_command.raw)
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

    updateTestOp(currentRunningTest, currentRunningTest["id"])

    time.sleep(2)

    file_name = "memory-" + \
        str(data['memory']) + "_" + str(data['voltage']) + \
        "V-" + "_dst-" + \
        str(currentRunningTest['dataSetupTime']) + \
        "_" + str(currentRunningTest['id']) + "_" + str(currentRunningTest['iteration'])

    save_data_csv(["Address", "Value"], values, file_name,
                  currentRunningTest)



def split_list_into_matrix_carry(my_list, cols, default=None):
    rows = math.ceil(len(my_list) / cols)
    print("cols", cols)
    matrix = []

    for i in range(cols):
        row = my_list[i * cols: (i + 1) * cols] + [default] * \
            (cols - len(my_list[i * cols: (i + 1) * cols]))
        matrix.append(row)

    return matrix


def save_data_csv(header, values, file_name, currentRunningTest):
    #current_directory = os.getcwd()
    file_path = os.path.join("assets/csv_files", file_name+".csv")

    # Open the CSV file for writing
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the data to the CSV file
        writer.writerow(header)
        for address, item in enumerate(values):
            row = [address, item]
            writer.writerow(row)

    currentRunningTest["fileName"] = file_path
    updateTestOp(currentRunningTest, currentRunningTest["id"])

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
    ##all_data = pd.concat([pd.read_csv(f) for f in csv_files])
    tests_id_list = [item["id"] for item in request.data]
    id_string = "_".join([str(tests_id_list[0]), str(tests_id_list[-1])])
    # print(test_ids)

    file_name = "memory_FRAM_12.0V-xxx_" + id_string
    print(file_name)
    # Name of the column to generate the heatmap for
    ##column_name = 'Value'

    # Create a list of lists with some data
    ##values = all_data[column_name].tolist()
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
    #cbar = ax.collections[0].colorbar
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

    ##data["fileName"] = file_name_png
    ##updateTestOp(data, testOpId)
    path = os.path.join(settings.MEDIA_ROOT, file_name_png)

    with default_storage.open(path) as f:
        response = HttpResponse(f.read(), content_type='image/png')
        #response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# other metrics


@api_view(["POST"])
def getMetrics(request):
    # Return the image file as an HTTP response
    prYellow("---------------------------------------------")
    '''
    for data in request.data:
        if data["fileName"] == "a123.csv":
            #data["fileName"] = "a12.csv"
            file_name = "memory-" + \
            str(data['memory']) + "_12V-" + "_dst-" + \
        str(data['dataSetupTime']) + \
        "_" + str(data['testOp_id']) + "_" + str(data['iteration'])
            curr_data = data
            file_path = os.path.join("assets/csv_files", file_name+".csv")
            curr_data["fileName"] = file_path
            updateTestOp(curr_data, data["testOp_id"])
            #print(data['testOp_id'])
    '''

    prGreen("------------------Get Metrics-----------------")

    data_df = pd.DataFrame(request.data).reset_index(drop=True)
    print(data_df)
    prGreen("-----------------UNIFORMITY--------------------")
    uniformity = []

    # Group the DataFrame by 'Memory Type'
    grouped_by_memory = data_df.groupby(['memory'])
    for memory, chip_group in grouped_by_memory:
        grouped_dst = chip_group.groupby(['dataSetupTime'])
        chip_measurements = []
        for dst, group in grouped_dst:
            dataSetupTime = dst
            challenge_measurements = []
            for index, row in group.iterrows():
                chip_data = {}
                chip_data = row.to_dict()
                mem_response = PUFProcessor.read_and_store_input_data(chip_data["fileName"])
                chip_data['hammingWeight'] = PUFProcessor.hamming_weight(mem_response)
                chip_data['ones'], chip_data['zeors'] = PUFProcessor.calculate_ones_and_zeros(mem_response)
                challenge_measurements.append(chip_data)
            
            chip_measurements.append({'challengeName': "data setup time", 'challengeValue':dataSetupTime, 'challengeMeasurements':challenge_measurements })

        uniformity.append({"chip" : memory , "chipMeasurements" : chip_measurements})

    data = [(item['id'], item["fileName"]) for item in request.data]

    prGreen("-----------------ROBUSTNESS-------------------")

    intra_hd_list = []
    for memory, memory_group in data_df.groupby("memory"):
        chip_measurements = []
        
        for dst, dst_group in memory_group.groupby('dataSetupTime'):
            hd_list_single_device_challenge = []
            if len(dst_group) > 1:
                for row1 in dst_group.itertuples(index=True):
                    for row2 in dst_group.loc[row1.Index+1:].itertuples(index=True):
                        puf_response_1 = PUFProcessor.read_and_store_input_data(row1.fileName)
                        puf_response_2 = PUFProcessor.read_and_store_input_data(row2.fileName)
                        hd_list_single_device_challenge.append(PUFProcessor.hamming_distance(puf_response_1, puf_response_2))
            
                print(hd_list_single_device_challenge)
                data = {'challengeName': "data setup time",
                        'challengeValue':dst,
                        'Robustness': True,
                        'hammingDistance': {
                                "min":min(hd_list_single_device_challenge),
                                'max':max(hd_list_single_device_challenge),
                                'avg':statistics.mean(hd_list_single_device_challenge)
                        } }
                #chip_measurements.append(data)
            
            else:
                data = {'challengeName': "data setup time",
                        'challengeValue':dst,
                        'Robustness': False,
                        'hammingDistance': {
                                "min":None,
                                'max':None,
                                'avg':None
                        } }
            
            chip_measurements.append(data)

        intra_hd_list.append({"chip" : memory , "chipMeasurements" : chip_measurements})
    
    prGreen("-----------------Uniqueness-------------------")

    print(data_df)

    for memory, memory_group in data_df.groupby("memory"):
        print(len(memory))
        print(memory)
        print(len(memory_group))
        print(memory_group)
        #pass



    uniqueness_data = [{ 'challengeName': "data setup time",
                        'challengeValue':15,
                        'hammingDistances': [ {
                                "chip_1": "R1",
                                "chip_2": "R2",
                                "chip_1_iteration": 0,
                                "chip_2_iteration": 0,
                                "inter_hd":0.5
                        },
                        {
                                "chip_1": "R1",
                                "chip_2": "R2",
                                "chip_1_iteration": 0,
                                "chip_2_iteration": 1,
                                "inter_hd":0.7
                        },
                        {
                                "chip_1": "R1",
                                "chip_2": "R2",
                                "chip_1_iteration": 0,
                                "chip_2_iteration": 2,
                                "inter_hd":0.6
                        }
                        ] },
                        { 'challengeName': "data setup time",
                        'challengeValue':14,
                        'hammingDistances': [ {
                                "chip_1": "R1",
                                "chip_2": "R2",
                                "chip_1_iteration": 0,
                                "chip_2_iteration": 0,
                                "inter_hd":0.5
                        }
                        ] }
                        ]

    inter_hd_list = []
    inter_hd_list.append({"chips": ["R1", "R2"], "uniquenessMeasurments": uniqueness_data})




    prYellow("---------------------------------------------")
    
    # Create a list of lists with some data
    evaluation_list = []

    evaluation_list.append({
        'uniformity': uniformity,
        'intra_hd_list': intra_hd_list,
        'inter_hd_list': inter_hd_list
    })

    return Response(evaluation_list)


'''def hamming_distance(puf1, puf2):
    """
    Calculate the Hamming distance between two binary strings (PUFs).
    """
    if len(puf1) != len(puf2):
        raise ValueError("PUFs must have the same length.")

    # Count the number of differing bits
    diff = 0
    for i in range(len(puf1)):
        if puf1[i] != puf2[i]:
            diff += 1

    return diff
'''

@api_view(["GET"])
def getImage(request, file_name):
    # Return the image file as an HTTP response
    print("-----------")
    print(file_name)
    print("-----------")
    path = os.path.join(settings.MEDIA_ROOT, file_name)

    with default_storage.open(path) as f:
        response = HttpResponse(f.read(), content_type='image/png')
        #response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

