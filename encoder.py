from enum import Enum


class Types(Enum):
    COORDINATE = 1
    MESSAGE = 2
    DISCONNECT = 3
    CONNECT = 4
    DEATH = 5
    KILL = 6


def intToBytes(org_num, nbytes):
    bytes = bytearray()
    num = org_num
    for i in range(nbytes):
        bytes.append(num & 255)
        num = num >> 8

    return bytes


def bytesToInt(bytes, startIdx, endIdx):
    if endIdx - startIdx > 4:
        print("You cannot convert more than 4 bytes to an integer.")
        return 0
    num = 0
    subbytes = bytes[startIdx:endIdx]
    for byte in subbytes[::-1]:
        num |= byte
        num = num << 8

    return num >> 8



class Encoder:
    def __init__(self):
        self.bytes = bytearray()

    def setStrData(self, data):
        encoded_data = data.encode('utf-8')
        length_bytes = intToBytes(len(encoded_data), 2)
        self.bytes += length_bytes
        # Add two empty bytes which the server can fill with player id.
        self.bytes += intToBytes(0, 2)
        self.bytes += intToBytes(Types.MESSAGE.value, 1)
        self.bytes += encoded_data

    def setCoordData(self, coord, score):
        length_bytes = intToBytes(6, 2)
        # Create bytestream from the given data.
        self.bytes += length_bytes
        # Add two empty bytes which the server can fill with player id.
        self.bytes += intToBytes(0, 2)
        self.bytes += intToBytes(Types.COORDINATE.value, 1)
        self.bytes += intToBytes(int(coord.x), 2)
        self.bytes += intToBytes(int(coord.y), 2)
        self.bytes += intToBytes(int(score), 2)

    def setDeathData(self):
        length_bytes = intToBytes(5, 2)
        # Create bytestream from the given data.
        self.bytes += length_bytes
        # Add two empty bytes which the server can fill with player id.
        self.bytes += intToBytes(0, 2)
        self.bytes += intToBytes(Types.DEATH.value, 1)

    def setKillData(self, score):
        length_bytes = intToBytes(7, 2)
        # Create bytestream from the given data.
        self.bytes += length_bytes
        # Add two empty bytes which the server can fill with player id.
        self.bytes += intToBytes(0, 2)
        self.bytes += intToBytes(Types.KILL.value, 1)
        self.bytes += intToBytes(score, 2)

    def getBytes(self):
        data = self.bytes
        self.bytes = bytearray()
        return data

    def showBytes(self):
        print(self.bytes)


class Decoder:
    def __init__(self):
        self.bytes = bytearray()

    def addData(self, bytes):
        self.bytes += bytes

    # Returns 1 if there is a complete message in the buffer.
    def processData(self):
        if len(self.bytes) < 5:
            return 0

        self.data_length = bytesToInt(self.bytes, 0, 2)
        self.data_sender = bytesToInt(self.bytes, 2, 4)
        self.data_type = bytesToInt(self.bytes, 4, 5)
        if len(self.bytes) < 5 + self.data_length:
            # There has not yet been received enough data to process all of this data.
            return 0
        return 1

    def getDataType(self):
        return self.data_type

    def getData(self):
        if self.data_type == Types.COORDINATE.value:
            # Returns tuple of the form (x, y, score)
            data = self.data_sender, bytesToInt(self.bytes, 5, 7), bytesToInt(self.bytes, 7, 9), bytesToInt(self.bytes, 9, 11)
            # Remove processed data.
            self.bytes = self.bytes[11:]
            return data

        if self.data_type == Types.MESSAGE.value:
            data = self.bytes[5:5 + self.data_length].decode('utf-8')
            self.bytes = self.bytes[5 + self.data_length:]
            return data

        if self.data_type == Types.KILL.value:
            # Returns tuple of the form (x, y, score)
            data = bytesToInt(self.bytes, 5, 7)
            # Remove processed data.
            self.bytes = self.bytes[7:]
            return data

        if self.data_type == Types.DEATH.value:
            self.bytes = self.bytes[5:]
            return None

    def getBytes(self):
        if self.data_type == Types.COORDINATE.value:
            data = self.bytes[0:5 + self.data_length]
            self.bytes = self.bytes[5 + self.data_length:]
        elif self.data_type == Types.MESSAGE.value:
            data = self.bytes[0:11]
            self.bytes = self.bytes[11:]
        return data
