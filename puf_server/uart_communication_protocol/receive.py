#from .interface import Interface
from .uart_frame_protocol import Frame
from .command import Command
from .command import data2str
from .command import str2data
from time import sleep
# importing redis
import redis

pool = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
redis = redis.Redis(connection_pool=pool)

#attempts = 0


class ReceiveError(Exception):
    pass


class Receive:
    def __init__(self, interface):
        self.interface = interface
        self.attempts = 0

    def receive_frame(self, attempts, remaining) -> Frame:
        self.attempts = attempts
        self.remaining = remaining
        print('\033[91m>>>> RECEIVE :: Read From STM32 \033[00m')

        raw_bytes, rem_frames = self.interface.read_to_idle(
            self.attempts, self.remaining)  # read from stm32
        
        while raw_bytes == [[]]:

            if self.attempts > 3:
                redis.set("stm32:state", "open")
                raise ReceiveError
            else:
                self.attempts += 1
                print('attemp {}'.format(self.attempts))
                #print('attempt ', self.attempts)
                sleep(1)
                raw_bytes = self.interface.read_to_idle()  # read from stm32
                print('Receive:')
                print(raw_bytes)
                print(len(raw_bytes))
                print(type(raw_bytes))
            # read nothing here
            #raw_bytes = self.interface.read_to_idle()
            # TODO: should detect ack response instead

        return raw_bytes, rem_frames  # check validity of the frame

        # return raw_bytes
