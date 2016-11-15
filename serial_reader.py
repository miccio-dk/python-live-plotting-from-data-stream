import serial
import numpy as np


class Reader(object):
    """ Sets up socket server that data streaming clients can connect to """
    # Use some random port

    def __init__(self, port="/dev/ttyUSB0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port)
        self.ser.baudrate = baudrate

    def closeConnection(self):
        self.ser.close()

    def __call__(self, label=None, raw=False, dtype=float):
        """ label: data group label
            raw: if true returns the data as it was read (string)
            dtype: data type that the data is converted to if raw is false """
        while True:
            rawData = self.ser.readline()
            try:
                decodedData = rawData.decode()
            except UnicodeDecodeError:
                print(rawData)
                continue

            if raw:
                # return whatever was received
                return rawData

            try:
                # Interpret the received data
                splittedData = decodedData.split(',')
                if label is None or label == splittedData[0]:
                    return splittedData[0], np.array(list(map(dtype, splittedData[1:])))
            except ValueError:
                if len(splittedData) > 1:
                    return splittedData[0], splittedData[1:]
            print(rawData)


if __name__ == '__main__':
    reader = Reader()

    while True:
        print(reader())
