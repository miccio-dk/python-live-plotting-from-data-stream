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

    def __call__(self, label=None, raw=False, dtype=int):
        """ label: data group label
            raw: if true returns the data as it was read (string)
            dtype: data type that the data is converted to if raw is false """
        while True:
            # Read one byte at a time
            rawData = self.ser.readline()
            
            if raw:
                # return whatever was received
                return rawData

            try:
                # Interpret the received data
                splittedData = rawData.split(',')
                if label is None or label == splittedData[0]:
                    return splittedData[0], np.array([*map(dtype, splittedData[1:])])
            except ValueError:
                pass
            print(rawData)

if __name__ == '__main__':
    reader = Reader()

    while True:
        print(reader())