import zlib


class InvalidError(Exception):
    pass


class Frame:
    """
    +--------------+----------------+--------------------+----------------+--------------+
    | 0x55(1 byte) | length(1 byte) | data(length bytes) | crc32(4 bytes) | 0xaa(1 byte) |
    +--------------+----------------+--------------------+----------------+--------------+
    """

    def __init__(self, frame):
        self.data = self.check_valid(frame)
        self.raw = frame

    @staticmethod
    def get_crc(data):
        crc = zlib.crc32(bytes(data))
        crc_data = [(crc >> i & 0xFF) for i in (24, 16, 8, 0)]
        return crc_data

    def check_valid(self, frame):
        # print(f'\033[91m>> check frame validity \033[00m {frame}')
        if frame[0] != 171:
            print(frame)
            raise InvalidError("wrong start (Header 1)", frame)

        elif frame[1] != 205 and frame[1] != 239:
            raise InvalidError("wrong start (Header 2)", frame)
        elif frame[-2] != 225:
            raise InvalidError("wrong end (Trailer 1)", frame)
        elif frame[-1] != 226:
            raise InvalidError("wrong end (Trailer 2)", frame)
        length = frame[2]
        if len(frame) != (1 + 1 + 1 + length + 1 + 1):
            raise InvalidError("wrong length", frame)

        if frame == []:
            return frame
        else:
            length = frame[2]
            data = frame[3: (length + 3)]
            # data = frame[3: -2]
            ''' TODO
                crc_array = frame[-5:-1]
                if crc_array != Frame.get_crc(data):
                raise InvalidError("wrong crc")
            '''

        return data

    @staticmethod
    def build_frame(data):
        if len(data) == 0:
            raise InvalidError("0 length data")
        result = [0x55]
        result.append(len(data))
        result += data
        crc_array = Frame.get_crc(data)
        result += crc_array
        result.append(0xAA)
        return Frame(result)
