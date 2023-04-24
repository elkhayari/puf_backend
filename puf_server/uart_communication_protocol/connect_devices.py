import glob
import serial
from django.http import HttpResponse
from .command import Command, data2str, str2data
from .uart_frame_protocol import Frame
from .receive import Receive
from .uart_serial import UartInterface
import json


class MyClass:
    def __init__(self, name):
        self.name = name

class SerialCommunication():
    uart_instances = []

    def __init__(self):
        print("\033[91m>> Get Connected Devices ...\033[00m")
        self.uart_instances = []
        self.connect_to_board()

    def connect_to_board(self):
        stm32_ports = []
        # Iterate through each port and check if it contains "ACM"
        for port in glob.glob('/dev/tty*'):
            if "ACM" in port:
                stm32_ports.append(port)
        
    
        # Try to connect to the first available port
        for port in stm32_ports:
            try:
                # Set up the serial port
                print(f"try port {port } \n")
                attempts = 0
                rem_frames = []
                uart_instance = UartInterface(port)
                
                ##ser = serial.Serial(port, 115200, timeout=10)
                ##ser.reset_input_buffer()
                ##ser.reset_output_buffer()

                receive = Receive(uart_instance)
                
                
                idn_command = Command.build_idn_command()

                # Production mode
                # Send a message to the board
                ##uart_instance.serial.write(idn_command.raw)
                ##received_frame, rem_frames = receive.receive_frame(attempts, rem_frames)
                ###print("received frame\n")
                # TODO more dynamic

                ###print(f"len(received_frame) == {len(received_frame)} {received_frame}")
                
                ###if len(received_frame) > 0:
                if  True:
                    '''received_frame = Frame(received_frame[0])

                    payload = data2str(received_frame.data)
                    print('Payload')
                    print(payload)

                    if received_frame.data == []:
                        data = [{
                                'id': 'id',
                                'name': 'name',
                                'ExternalMemory': 'externalMemory',
                                'is_ctive': False,
                                }]
                    else:
                        res = json.loads(payload)
                        data = [{
                                'id': res['key'],
                                'name': res['name'],
                                'ExternalMemory': res['externalMemory'],
                                'is_ctive': True,
                            }] '''

                    
                    customized_name = "my_instance_1"
                    
                    globals()[customized_name] = uart_instance
                    self.uart_instances.append(uart_instance)
                   

                    #print("Let see")
                    #receive2 = Receive(self.uart_instances[0])
                    #received_frame, rem_frames = receive2.receive_frame(attempts, rem_frames)


                    #uart_instance.serial.close()


                else:
                    print("No device Detected for this port")
            
                # Return the response to the client
                #return HttpResponse(f"Connected to board on {port}. Board responded with: {response}")
            except serial.SerialException:
                # If the port cannot be opened, try the next one
                pass