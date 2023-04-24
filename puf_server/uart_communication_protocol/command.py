import json

TEST_COMMAND = "TEST"
STATE_COMMAND = "STATE?"
RESULT_COMMAND = "RESULT?"
PAYLOAD_COMMAND = '{"key" : "123456", "name":"STM32F429", "externalMemory": "SRAM"}'
#IDN_COMMAND = "IDN?"
IDN_COMMAND = '{"HEADER":"*IDN?", "params_size":0}'
WRITE_READ_FRAM_COMMAND = "RWF"
END_READ = "END_READ"
CUSTOM = "CUSTOM"


class InvalidError(Exception):
    pass


def data2str(data):
    return "".join(chr(i) for i in data)


def str2data(str):
    return [ord(x) for x in str]


class Command:
    def __init__(self, command, payload=None):
        if command == TEST_COMMAND:
            if payload == None:
                raise InvalidError
            self.command = TEST_COMMAND
            command_str = command + json.dumps(payload)
            self.raw = str2data(command_str)
        elif command == STATE_COMMAND:
            if payload != None:
                raise InvalidError
            self.command = STATE_COMMAND
            command_str = command
            self.raw = str2data(command_str)
            print(
                "{} raw --> \033[92m {}\033[00m" .format(command_str, self.raw))
        elif command == RESULT_COMMAND:
            if payload != None:
                raise InvalidError
            self.command = RESULT_COMMAND
            command_str = command
            self.raw = str2data(command_str)
            print(
                "{} raw -> \033[92m {}\033[00m" .format(command_str, self.raw))
        elif command == PAYLOAD_COMMAND:
            self.raw = str2data(command)
        elif command == IDN_COMMAND:
            self.raw = str2data(command)
        elif command == WRITE_READ_FRAM_COMMAND:
            self.raw = str2data(command)
        elif command == END_READ:
            self.raw = str2data(command)
        elif command == CUSTOM:
            if payload == None:
                raise InvalidError
            self.command = CUSTOM
            command_str = command
            self.raw = str2data(str(payload))
        else:
            raise InvalidError

    @staticmethod
    def build_test_command(payload):
        return Command(TEST_COMMAND, payload)

    @staticmethod
    def build_state_command():
        return Command(STATE_COMMAND)

    @staticmethod
    def build_result_command():
        return Command(RESULT_COMMAND)

    @staticmethod
    def build_payload_command():
        return Command(PAYLOAD_COMMAND)

    @staticmethod
    def build_idn_command():
        return Command(IDN_COMMAND)

    @staticmethod
    def build_rwf_command():
        return Command(WRITE_READ_FRAM_COMMAND)

    @staticmethod
    def build_end_read_command():
        return Command(END_READ)

    @staticmethod
    def build_custom_payload(payload):
        return Command(CUSTOM, payload)
