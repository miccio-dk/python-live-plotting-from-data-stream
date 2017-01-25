import sys
import numpy as np


class Reader(object):
    def closeConnection(self):
        pass

    def write(self, data):
        print("Can not write data to server when using pipe reader.\nMessage: '{:}' has been discarded".format(data))

    def __call__(self, label=None, raw=False, dtype=float):
        """ label: data group label
            raw: if true returns the data as it was read (string)
            dtype: data type that the data is converted to if raw is false """
        while True:
            rawData = sys.stdin.readline()
            if raw:
                # return whatever was received
                return rawData

            try:
                # Interpret the received data
                splittedData = rawData.split(',')
                if label is None or label == splittedData[0]:
                    return splittedData[0], np.array(list(map(dtype, splittedData[1:]))), True
            except ValueError:
                if len(splittedData) > 1:
                    return splittedData[0], splittedData[1:], False
            return rawData, [], False


if __name__ == '__main__':
    reader = Reader()

    while True:
        s, data = reader()
        print(s, data)
