from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from .models import TtyDeviceModel
from .serializers import TtyDeviceSerializer
from rest_framework.views import APIView
from puf_server.uart_communication_protocol.uart_serial import UartInterface
from puf_server.uart_communication_protocol.receive import Receive
from puf_server.uart_communication_protocol.command import Command
from puf_server.uart_communication_protocol.uart_frame_protocol import Frame
from puf_server.uart_communication_protocol.command import Command, data2str
import json
import threading
from rest_framework.decorators import api_view
from django.utils import timezone
import time


class TestViewOperationsSet(viewsets.ViewSet):

    def list(self, request):
        print('LIST OF DEVICES:')
        device = TtyDeviceModel.objects.all()
        serializer = TtyDeviceSerializer(device, many=True)
        return Response(serializer.data)

    def create(self, request):
        print("CREATE A TEST OPERATION:")
        print('add a device', request.data)
        serializer = TtyDeviceModel(data=request.data)
        print('is_valide', serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        print('RETRIEVE A TEST OPERATIO:')
        queryset = TtyDeviceModel.objects.all()
        device = get_object_or_404(queryset, pk=pk)
        serializer = TtyDeviceSerializer(device)
        return Response(serializer.data)

    def update(self, request, pk=None):
        print("UPDATE TEST OPERATION:")
        device = TtyDeviceModel.objects.get(pk=pk)
        serializer = TtyDeviceSerializer(device, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        print('- DELETE a TEST OPERATION')
        device = TtyDeviceModel.objects.get(pk=pk)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InsertedDevicesAPI(APIView):
    def get(self, request):
        inserted_devices = TtyDeviceModel.objects.filter(is_connected=False)
        serializer = TtyDeviceSerializer(inserted_devices, many=True)
        return Response(serializer.data)


class ConnectedDevicesAPI(APIView):
    def get(self, request):
        connected_devices = TtyDeviceModel.objects.filter(is_connected=True)
        serializer = TtyDeviceSerializer(connected_devices, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def connect_device_by_port(request):
    port = request.GET.get('port')
    print('port:', port)

    # Perform the serial communication with the STM32 board using the provided port
    # Define a function to perform the serial communication and update the model
    def perform_serial_communication():
        attempt = 0
        rem_frames = []
        try:
            uart_instance = UartInterface(port)
            receive_instance = Receive(uart_instance)
            idn_command = Command.build_idn_command()

            # Perform communication with the STM32 board as per your requirements
            uart_instance.write(idn_command.raw)
            received_frame, rem_frames = receive_instance.receive_frame(
                attempt, rem_frames)

            print(received_frame)
            print(rem_frames)
            if received_frame == []:
                print('frame empty')
                callback({'status': 'failed', 'type': 'warning',
                         'message': f"Failed to open port {port}. Please, FLASH/DEBUG your board"})
            else:
                received_frame = Frame(received_frame[0])

                data = data2str(received_frame.data)
                print('pyaload ', data)

                payload = json.loads(data)

                # Update the TtyDeviceModel with the received data
                try:
                    device = TtyDeviceModel.objects.get(device_port=port)
                    device.is_connected = True
                    device.device_name = payload['name']
                    device.owner = payload['owner']
                    device.serial_number = payload['serial']
                    device.device_label = payload['device_label']
                    device.connected_since = timezone.now()
                    device.save()
                    callback({'status': 'connected',
                              'message': f"Device {payload['device_label']} connected."})

                except TtyDeviceModel.DoesNotExist:
                    # callback if the device record doesn't exist
                    callback({'status': 'failed', 'type': 'error',
                             'message': 'Device does not exist'})

        except Exception as e:
            print(f"Failed to open port: {e}")
            callback({'status': 'failed', 'type': 'error', 'message': str(e)})

    # Define a function to call the perform_serial_communication in a separate thread

    def connect_in_thread():
        perform_serial_communication()

    try:
        # Create an event to synchronize the thread
        event = threading.Event()

        # Create a variable to store the response data
        response_data = {}

        # Define the callback function
        def callback(data):
            nonlocal response_data
            response_data = data
            event.set()

        # Create a new thread and start it
        thread = threading.Thread(target=connect_in_thread)
        thread.start()

        # Wait for the event to be set, indicating that the serial communication is complete
        event.wait()

        return Response(response_data)

    except Exception as e:
        print(f"Failed to open port: {e}")
        return Response({'status': 'failed', 'type': 'error', 'message': str(e)})
