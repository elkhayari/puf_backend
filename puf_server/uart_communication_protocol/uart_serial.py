# -*- coding: utf-8 -*-

import serial
from multiprocessing import  Queue
#from .interface import Interface
import time
from .command import Command

READ_TIMEOUT = 3

c = Command

#q = Queue()


def prYellow(skk): print("\033[93m{}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m{}\033[00m" .format(skk))

'''TODO add this exception-- serial.serialutil.SerialException: 
            device reports readiness to read but returned no data 
            (device disconnected or multiple access on port?
'''

class UartInterface():
    def __init__(self, port):
        self.serial = serial.Serial(port, 115200, timeout=10)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        print("\033[91m>> Serial connection ...\033[00m")
        print(f"{self.serial} \n")
        self.remaining_bytes = 1
        self.remaining_data = []
        self.queue = Queue()
    

    def read(self, length=1):
        data = self.serial.read(length)
        print("received: ", data)
        return data

    def read_one_byte(self, remaining_bytes, last_remaining_frames):
        #print("*** read_one_byte() ***")
        if remaining_bytes == 0:
            remaining_bytes = 1

        self.remaining_bytes = remaining_bytes
        self.remaining_data = last_remaining_frames
        data = self.serial.read(self.remaining_bytes)
        #print("data ", data)
        self.remaining_bytes = self.serial.inWaiting()

        return (data, self.remaining_bytes)

    def read_to_idle(self, attempts, last_remaining_frames):
        # read until timeout
        prPurple("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        result = []
        self.remaining_data = last_remaining_frames
        self.remaining_bytes = 1
        
        q = Queue()

        innerAttempts = 0

        while self.remaining_bytes > 0 or innerAttempts < 3:
            #print(f"* Remaining_bytes {self.remaining_bytes}")
            #print(f"* remaining_data {self.remaining_data}")
            data, self.remaining_bytes = self.read_one_byte(
                self.remaining_bytes, last_remaining_frames)

            for b in list(data):
                q.put(b)

            if self.remaining_bytes == 0:
                time.sleep(0.1)
                innerAttempts += 1
            else:
                # Initialize the number of attempts
                innerAttempts = 0

        print("\033[91m\n**Empty the queue ...\033[00m")
        print(f"-- size of the queue:  {q.qsize()} \n")
        
        # retrieve data from the global queue
        while q.qsize() > 0:
            data = q.get()
            result.append(data)

        frames, self.remaining_data = self.extractFrames(
            self.remaining_data + result)

        #print(f"number of frames {len(frames)}")
        #print(f"number of rem frames {len(self.remaining_data)}")

        #prPurple("<><><><><><><><><><><><><><><>")
        #print(frames)
        #print(self.remaining_data)
        #prPurple("<><><><><><><><><><><><><><><>")
        prPurple("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return frames, self.remaining_data

    def write(self, raw_bytes):
        print('\n-------------------------------------------------')
        print("\033[94m**__Write To Stm32__**\033[00m >> {}".format(raw_bytes))
        print('-------------------------------------------------\n')
        self.serial.write(raw_bytes)

    def extractFrames(self, raw_bytes):
        """
        extract frames from a list containing a sequence of frames, this funtion 
        extracts frames based on start flag '171' 
        The code uses two list comprehension to find the index of the first and last
        occurence of the start and end values respectively, then it uses the zip function
        to match the indexes and slice the list. The output is a list of lists that 
        contain the sublists that starts with the start value and ends with the end value.
        """
        print('Extract frames')
        print(f"-- length = {len(raw_bytes)}")

        frames = [raw_bytes[i:j+1] for i, j in zip([i for i, x in enumerate(
            raw_bytes) if x == 171], [i for i, x in enumerate(raw_bytes) if x == 226])]

        length_frames = self.nested_array_length_sum(frames)
        rest = raw_bytes[length_frames:]

        return frames, rest

    # Function to find sum of lengths of nested arrays
    def nested_array_length_sum(self, arr):
        total = 0
        for item in arr:
            if type(item) == list:
                total += len(item)
        return total


    '''def read_one_byte_custum(self, attempts, last_remaining_frames):
        print(f"read one byte cutom {attempts}")
        data_1 = [[171, 205, 7, 87, 82, 73, 84, 73, 78, 71, 225, 226],
                  [171, 205, 11, 69, 78, 68, 32, 87,
                      82, 73, 84, 73, 78, 71, 225, 226],
                  [171, 205, 7, 82, 69, 65, 68, 73, 78, 71, 225, 226,
                  171, 239, 1, 1, 225, 226, 171, 239, 1, 1, 225, 226,
                  171, 239, 1, 1, 225, 226, 171, 239, 1, 1, 225, 226,
                  171, 239, 1, 1, 225, 226, 171, 239, 1, 1, 225, 226,
                  171, 239, 1, 1, 225, 226, 171, 239, 1, 1, 225, 226,
                  171, 205, 11, 69, 78, 68, 32, 82, 69, 65, 68, 73], [78, 71, 225, 226],
                  [171, 205, 6, 70, 73, 78, 73, 83, 72, 225, 226]]

        data = last_remaining_frames + data_1[attempts]
        self.remaining_data_buffer = 0

        return (data, self.remaining_data_buffer)'''
