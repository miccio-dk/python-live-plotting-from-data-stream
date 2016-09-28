import sys
import numpy as np


class Reader(object):
    def closeConnection(self):
        pass

    def __call__(self, label=None, raw=False, dtype=int):
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
                    return splittedData[0], np.array(list(map(dtype, splittedData[1:])))
            except ValueError:
                pass
            print(rawData)


if __name__ == '__main__':
    reader = Reader()

    while True:
        s, data = reader()
        print(s, data)
