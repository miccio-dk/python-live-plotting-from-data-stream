import serial
import select
import struct
import numpy as np


# binary format: 
#   Np D_1 D_2 ... D_n CS \n
#   - Np    1B plot ID
#   - D_n   4B data value IEEE745
#   - CS    1B overall checksum
# 
# TODO:
# - add plot and signal labels
# - add different encodings (uint, int, etc)


def calcCrc(s):
    crc = 0
    for c in s:
        crc ^= c
    return crc


class Reader(object):
    """ Sets up serial server that data streaming clients can connect to """
    # Use some random port

    def __init__(self, port="/dev/ttyUSB0", baudrate=57600):
        print("using serial_reader_with_crc_binary")
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port)
        self.ser.baudrate = baudrate

    def closeConnection(self):
        self.ser.close()

    def write(self, data):
        print('Writing: "{:}"'.format(data.strip()))
        self.ser.write(data.encode("utf-8"))

    def __call__(self, label=None, raw=False, dtype=float):
        """ label: data group label
            raw: if true returns the data as it was read (string)
            dtype: data type that the data is converted to if raw is false """
        while True:
            if select.select([self.ser], [], [], 0.02)[0]:
                rawData = self.ser.readline()
            else:
                rawData = b''
                break;

            if raw:
                # return whatever was received
                return rawData

            # convert string into sequence of bytes
            byteData = bytearray()
            byteData.extend(rawData)
            # extract number of data points
            pointsN = (len(byteData) - 3) / 4
            if pointsN < 0 or pointsN > int(pointsN):
                print("points dont match ", pointsN)
                return rawData, [], False
            pointsN = int(pointsN)
            # extract plot ID (label), data points, and checksum
            fmt = "=B{0}fBx".format(pointsN)
            labelRead, *dataPoints, crcRead = struct.unpack(fmt, byteData)
            # calculate checksum
            crcCalc = calcCrc(rawData[:-2])

            if crcCalc == crcRead:
                if label is None or label == labelRead:
                    return str(labelRead), np.array(list(map(dtype, dataPoints))), True
                else:
                    print("wrong label")
            else:
                print("wrong crc", crcCalc, crcRead)
            break
        return rawData, [], False


if __name__ == '__main__':
    reader = Reader()

    while True:
        data = reader()
        if data:
            print(data)
